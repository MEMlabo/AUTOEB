from copy import deepcopy
from datetime import datetime
from distutils.file_util import copy_file
import glob
from io import TextIOWrapper
from multiprocessing.pool import ThreadPool
import os
import random
from sys import stdout
from tarfile import open as opentar
from typing import Generator, TextIO, Tuple

from .catpv_result import CatpvResult
from .configuration import Configuration
from .consel_manager import ConselManager
from .consts import *
from .cui import CommandArguments
from .iqtree_manager import IqtreeManager
from .nnigen import read_tree, Tree
from .slh_data import SlhData
from .summary import SummaryInfo
from .value_range import ValueRange


class OperationManager:
    """AUTOEBの処理を担当します。
    """

    def __init__(self, args: CommandArguments) -> None:
        """OpeartionManagerの新しいインスタンスを初期化します。

        Args:
            args (CommandArguments): 引数
        """
        self.__args: CommandArguments = args
        self.__config: Configuration = Configuration.load()
        self.__logger: TextIO = stdout

    def execute(self) -> None:
        """処理を実行します。
        """
        start_time: datetime = datetime.now()
        SEQ_PATH: str = os.path.abspath(self.__args.get_out_file_path(INFILE_SEQ))
        TREE_PATH: str = os.path.abspath(self.__args.get_out_file_path(INFILE_TREE))
        SITELH_PATH: str = os.path.abspath(self.__args.get_out_file_path(OUTFILE_SITELH))
        ALL_TREE_PATH: str = os.path.abspath(self.__args.get_out_file_path(OUTFILE_ALL_TREES))

        actual_seed: int = random.randrange(1, 0x7FFFFFFF) if self.__args.seed == -1 else self.__args.seed  # Max: max value of 32-bit signed integer
        branch_range: ValueRange = self.__args.bipartition_range
        tree: Tree = read_tree(self.__args.tree_file, self.__args.tree_type)
        self.__output_indexed_tree(tree)
        bipartition_count: int = self.__get_nniable_bipartition_count(tree)

        if self.__args.seq_file != SEQ_PATH:
            copy_file(self.__args.seq_file, SEQ_PATH)
        if self.__args.tree_file != TREE_PATH:
            copy_file(self.__args.tree_file, TREE_PATH)

        bipartition_index = 0
        iqtree_manager = IqtreeManager(self.__config)
        if not self.__args.iqtree_params is None:
            iqtree_manager.load_other_params(self.__args.iqtree_params)
        consel_manager = ConselManager(self.__config)

        if not self.__args.redo and os.path.isfile(SITELH_PATH):
            print(f"Site likelyhood calculation is skipped ('{OUTFILE_SITELH}' already exists)", file=self.__logger)
        else:
            # generating NNI-trees
            print("Start generating NNI trees", file=self.__logger)
            print(f"ML tree and NNI trees are written in '{ALL_TREE_PATH}'", file=self.__logger)

            with open(ALL_TREE_PATH, "wt") as trees_io:
                # output ML tree
                tree.export(trees_io, self.__args.tree_type)
                trees_io.write("\n")

                # output NNI trees
                for nni_set in self.__iterate_nni_pairs(tree):
                    # skip if not at specified branch
                    if not bipartition_index in branch_range:
                        bipartition_index += 1
                        continue

                    print(f"  NNI-tree No. {bipartition_index}-1", file=self.__logger)
                    nni_set[1].export(trees_io, self.__args.tree_type)
                    trees_io.write("\n")

                    print(f"  NNI-tree No. {bipartition_index}-2", file=self.__logger)
                    nni_set[2].export(trees_io, self.__args.tree_type)
                    trees_io.write("\n")

                    # increment branch index
                    bipartition_index += 1

            print("Finish generating NNI trees", file=self.__logger)

            # execute IQ-TREE to calculate site likelihood value
            print("Start calculating site likelyhood value", file=self.__logger)
            operation_start: datetime = datetime.now()

            iqtree_manager.calc_sitelh(
                SEQ_PATH,
                self.__args.model,
                TREE_PATH,
                ALL_TREE_PATH,
                self.__args.iqtree_verbose,
                self.__args.redo,
                os.path.splitext(SITELH_PATH)[0],
                self.__args.threads,
                self.__args.out_dir)

            operation_end: datetime = datetime.now()
            print(f"Finish calculating site likelyhood value in {(operation_end - operation_start)}", file=self.__logger)

        sitelh: SlhData = SlhData.load(SITELH_PATH)

        # execute CONSEL to compare Log-likelihood
        print("Start CONSEL operations", file=self.__logger)

        # CONSEL runs in SINGLE thread
        # To run fast, CONSEL should be run in parallel
        actual_tree_index: int = 1
        ml_sitelh: SlhData = SlhData([sitelh[0]])
        with ThreadPool(processes=self.__args.threads) as pool:
            for bipartition_index in range(bipartition_count):
                # skip if not specified branch
                if not bipartition_index in self.__args.bipartition_range:
                    continue
                pool.apply_async(self.__invoke_consel, (consel_manager, SlhData.concat(ml_sitelh, sitelh[actual_tree_index:(actual_tree_index + 2)]), bipartition_index, bipartition_count, actual_seed))
                actual_tree_index += 2
            pool.close()
            pool.join()

        print("Finish CONSEL operation", file=self.__logger)

        catpv: CatpvResult
        bipartition_index = 0
        valid_nni = list[Tuple[float, Tree]]()
        for current in tree.iterate_all_branches():
            # skip if not specified branch
            if not bipartition_index in branch_range:
                bipartition_index += 1
                continue
            # parse CATPV file
            catpv = CatpvResult.load(self.__args.get_out_file_path(f"{bipartition_index}.catpv"))[0]
            # change branch name
            current.name = self.__format_output_branch_name(self.__args.out_format, current.name, self.__args.sig_level, catpv)
            nni: list[Tree] = [Tree(nni.find_root()) for nni in current.get_nni()]
            if self.__args.sig_level <= catpv.stat_nni1.au:
                valid_nni.append((catpv.stat_nni1.au, nni[1]))
            if self.__args.sig_level <= catpv.stat_nni2.au:
                valid_nni.append((catpv.stat_nni2.au, nni[2]))
            # increment branch index
            bipartition_index += 1

        tree.export(self.__args.get_out_file_path(OUTFILE_TREE), self.__args.tree_type)

        finish_time: datetime = datetime.now()

        # generate summary file
        summary = SummaryInfo(valid_nni, self.__args, finish_time - start_time, actual_seed)
        summary.write(self.__args.get_out_file_path(OUTFILE_SUMMARY))

        # process tmp files
        tmp_files: list[str] | Generator[str, None, None]
        if self.__args.output_tmp_files:
            with opentar(self.__args.get_out_file_path(OUTFILE_TMPZIP), "w:gz") as tario:
                fullpath: str
                # trees
                tario.add(ALL_TREE_PATH, OUTFILE_ALL_TREES)
                os.remove(ALL_TREE_PATH)
                # sitelh
                tmp_files = glob.glob("trees.*", root_dir=self.__args.out_dir)
                for file in tmp_files:
                    fullpath = os.path.join(self.__args.out_dir, file)
                    tario.add(fullpath, file)
                    os.remove(fullpath)
                bipartition_index = -1
                # CONSEL output
                for i in range(bipartition_count):
                    bipartition_index += 1
                    if not bipartition_index in branch_range:
                        continue
                    tmp_files = self.__iterate_all_tmpfiles(i)
                    for file in tmp_files:
                        fullpath = os.path.join(self.__args.out_dir, file)
                        tario.add(fullpath, file)
                        os.remove(fullpath)
        else:
            # trees
            os.remove(ALL_TREE_PATH)
            # sitelh
            tmp_files = [self.__args.get_out_file_path(f) for f in glob.glob("trees.*", root_dir=self.__args.out_dir)]
            for file in tmp_files:
                os.remove(file)
            # CONSEL output
            for i in range(bipartition_count):
                if not i in branch_range:
                    continue
                tmp_files = [os.path.join(self.__args.out_dir, f) for f in self.__iterate_all_tmpfiles(i)]
                for file in tmp_files:
                    os.remove(file)
        if os.path.isfile(os.path.join(self.__args.out_dir, "parameters")):
            os.remove(os.path.join(self.__args.out_dir, "parameters"))

    @staticmethod
    def __get_nniable_bipartition_count(tree: Tree) -> int:
        """NNI可能な二分岐をカウントします。

        Args:
            tree (Tree): 二分岐をカウントするTreeのインスタンス

        Returns:
            int: NNI可能な二分岐の個数
        """
        result: int = 0
        for _ in tree.iterate_all_branches():
            result += 1
        return result

    def __output_indexed_tree(self, tree: Tree) -> None:
        """internal nodeがインデックス化されたTREEファイルを出力します。

        Args:
            tree (Tree): インデックス化するTreeインスタンス（このインスタンス自体は改変されない）
        """
        clone: Tree = deepcopy(tree)
        index = 0
        for current in clone.iterate_all_branches():
            current.name = str(index)
            index += 1
        clone.export(self.__args.get_out_file_path(OUTFILE_INDEX_TREE), self.__args.tree_type)

    @staticmethod
    def __iterate_nni_pairs(tree: Tree) -> Generator[Tuple[Tree, Tree, Tree], None, None]:
        """最尤樹形とNNI樹形2つからなる組の一覧を列挙します。

        Args:
            tree (Tree): 処理するTreeのインスタンス

        Yields:
            Generator[Tuple[Tree, Tree, Tree], None, None]: 最尤樹形とNNI樹形2つからなる組の一覧を列挙するGeneratorのインスタンス
        """
        generator: Generator[Tree, None, None] = tree.iterate_all_nni_trees()
        ml: Tree = next(generator)
        while True:
            try:
                nni_1: Tree = next(generator)
                nni_2: Tree = next(generator)
                yield (ml, nni_1, nni_2)
            except StopIteration:
                return

    def __invoke_consel(self, consel_manager: ConselManager, slh_set: SlhData, branch_index: int, branch_count: int, seed: int) -> None:
        """CONSELを実行します。

        Args:
            consel_manager (ConselManager): CONSELを実行するクライアント
            slh_set (SlhData): AU検定にかけるツリーの尤度一覧
            branch_index (int): 枝番号
            branch_count (int): 枝数
            seed (int): シード値
        """
        operation_start = datetime.now()
        consel_log: TextIOWrapper
        catpv_outpath: str = self.__args.get_out_file_path(f"{branch_index}.catpv")

        # skip if IQ-TREE is executed (with log)
        if not self.__args.redo and os.path.isfile(catpv_outpath):
            print(f"  Operation No. {branch_index} / {branch_count - 1} has already done (skipped).", file=self.__logger)
            return

        # export
        slh_set.export(self.__args.get_out_file_path(f"{branch_index}.sitelh"))

        # execute CONSEL
        if not self.__args.redo and not os.path.isfile(catpv_outpath):
            if not self.__args.redo and not os.path.isfile(self.__args.get_out_file_path(f"{branch_index}.pv")):
                if not self.__args.redo and not os.path.isfile(self.__args.get_out_file_path(f"{branch_index}.rmt")):
                    # 1. makermt
                    with open(self.__args.get_out_file_path(f"{branch_index}-makermt.log"), "wt") as consel_log:
                        consel_manager.makermt(f"{branch_index}.sitelh", seed, self.__args.rell_boot, cwd=self.__args.out_dir, stdout=consel_log)
                # 2. consel
                with open(self.__args.get_out_file_path(f"{branch_index}-consel.log"), "wt") as consel_log:
                    consel_manager.consel(str(branch_index), cwd=self.__args.out_dir, stdout=consel_log)
            # 3. catpv
            with open(catpv_outpath, "wt") as consel_log:
                consel_manager.catpv(str(branch_index), cwd=self.__args.out_dir, stdout=consel_log)

        operation_end = datetime.now()
        print(f"  Operation No. {branch_index} / {branch_count - 1} finished in {(operation_end - operation_start)}", file=self.__logger)

    @staticmethod
    def __format_output_branch_name(fmt: str, src: str, sig_level: float, catpv: CatpvResult) -> str:
        """出力ツリーの枝名を取得します。

        Args:
            fmt (str): 枝名のフォーマット
            src (str): 元の枝名
            sig_level (float): 有意水準
            catpv (CatpvResult): IQTREEファイルの情報

        Returns:フォーマットされた枝名
        """
        max_au_p: float = max(catpv.stat_nni1.au, catpv.stat_nni2.au)
        au_bin: str = RESULT_OK if sig_level > max_au_p else RESULT_NG

        result: str = fmt.format(src=src, bin=au_bin, p=max_au_p)
        return result

    def __iterate_all_tmpfiles(self, index: int) -> Generator[str, None, None]:
        """インデックスに対応する中間ファイルを全て列挙します。

        Args:
            index (int): インデックス

        Yields:
            Generator[str, None, None]: indexに対応する枝の中間ファイル名を列挙するイテレータのインスタンス
        """
        yield from glob.glob(f"{index}.*", root_dir=self.__args.out_dir)
        yield from glob.glob(f"{index}-nni1.*", root_dir=self.__args.out_dir)
        yield from glob.glob(f"{index}-nni2.*", root_dir=self.__args.out_dir)
        yield f"{index}-makermt.log"
        yield f"{index}-consel.log"
