from datetime import timedelta
from io import StringIO
from typing import Any, Generator, Iterable, TextIO, Tuple, overload

from .consts import INFILE_SEQ, INFILE_TREE, OUTFILE_INDEX_TREE, OUTFILE_TREE
from .cui.command_arguments import CommandArguments
from .nnigen import Tree
from .nnigen.io.iohandler import TreeIOHandler


class SummaryInfo:
    """サマリーファイルの情報を表します。
    """

    def __init__(self, valid_tree: list[Tuple[float, Tree]], args: CommandArguments, time: timedelta, seed: int) -> None:
        """SummaryInfoの新しいインスタンスを初期化します。

        Args:
            valid_tree (list[Tuple[float, Tree]]): 棄却されなかったツリーとp値一覧
            args (CommandArguments): 引数情報
            seed (int): 乱数で使用したシード値
            time (deltatime): 実行時間
        """
        self.__nni: list[Tuple[float, Tree]] = list(valid_tree) or []
        self.__nni.sort(key=lambda x: x[0], reverse=True)
        self.__model: str = args.model
        self.__out_format: str = args.out_format
        self.__sig_lebel: float = args.sig_level
        self.__tree_type: TreeIOHandler = args.tree_type
        self.__input_seq: str = args.get_out_file_path(INFILE_SEQ)
        self.__input_tree: str = args.get_out_file_path(INFILE_TREE)
        self.__output_index: str = args.get_out_file_path(OUTFILE_INDEX_TREE)
        self.__result_tree: str = args.get_out_file_path(OUTFILE_TREE)
        self.__seed: int = seed
        self.__seed_generated: bool = args.seed == -1
        self.__rell_boot: int = args.rell_boot
        self.__time: timedelta = time

    @property
    def valid_nni_trees(self) -> list[Tuple[float, Tree]]:
        """棄却されなかったNNIツリー一覧を取得します。
        """
        return self.__nni

    @property
    def model(self) -> str:
        """進化モデルを取得します。
        """
        return self.__model

    @property
    def out_format(self) -> str:
        """枝名のフォーマットを取得します。
        """
        return self.__out_format

    @property
    def sig_level(self) -> float:
        """有意水準を取得します。
        """
        return self.__sig_lebel

    @property
    def input_tree_seq(self) -> str:
        """使用した配列のパスを取得します。
        """
        return self.__input_seq

    @property
    def input_tree_path(self) -> str:
        """使用したツリーのパスを取得します。
        """
        return self.__input_tree

    @property
    def output_indexed_tree_path(self) -> str:
        """出力されたインデックスのツリーファイルのパスを取得します。
        """
        return self.__output_index

    @property
    def output_result_tree_path(self) -> str:
        """結果のツリーファイルのパスを取得します。
        """
        return self.__result_tree

    @property
    def rell_boot(self) -> int:
        """RELL-Bootstrapの複製数を取得します。
        """
        return self.__rell_boot

    @property
    def seed(self) -> int:
        """シード値を取得します。
        """
        return self.__seed

    @property
    def total_time(self) -> timedelta:
        """処理にかかった時間を取得します。
        """
        return self.__time

    @overload
    def write(self, dest: TextIO) -> None:
        """サマリーファイルを出力します。

        Args:
            dest (TextIO): 出力先のストリームオブジェクト
        """
        ...

    @overload
    def write(self, dest: str) -> None:
        """サマリーファイルを出力します。

        Args:
            dest (TextIO): 出力先のファイルパス
        """
        ...

    def write(self, dest: str | TextIO) -> None:
        if isinstance(dest, str):
            with open(dest, "wt") as io:
                self.__write(io)
        else:
            self.__write(dest)

    def __write(self, dest: TextIO) -> None:
        """サマリーファイルを出力します。

        Args:
            dest (TextIO): 出力先のストリームオブジェクト
        """
        def writeline(value: Any = "") -> None:
            print(value, file=dest)

        def write_title(title: str) -> None:
            writeline(f"[{title}]")

        def write_entries(entries: Iterable[Tuple[str, Any]]) -> None:
            for (key, value) in entries:
                writeline(f"{key}: {value}")

        write_title("Summary")
        write_entries(self.__get_summary())
        writeline()

        write_title("Best tree")
        with open(self.input_tree_path, "r") as tree_io:
            writeline(tree_io.read(-1).strip())
        writeline()

        write_title("Not rejected NNI trees")
        writeline(f"p-value\ttree")
        for au, nni in self.valid_nni_trees:
            with StringIO() as str_io:
                nni.export(str_io, self.__tree_type)
                writeline(f"{au}\t{str_io.getvalue()}")
        writeline()

        write_title("Result tree")
        with open(self.output_result_tree_path, "r") as tree_io:
            writeline(tree_io.read(-1).strip())

    def __get_summary(self) -> Generator[Tuple[str, Any], None, None]:
        yield ("Substitution model", self.model)
        yield ("Significant level", self.sig_level)
        if self.__seed_generated:
            yield ("Seed", f"-1 ({self.seed})")
        else:
            yield ("Seed", self.seed)
        yield ("RELL-Bootstrap replicates", self.rell_boot)
        yield ("Branch name format", self.out_format)
        yield ("Not rejected NNI trees", len(self.__nni))
        yield ("Sequence file", self.input_tree_seq)
        yield ("Best tree file", self.input_tree_path)
        yield ("Branch index file", self.output_indexed_tree_path)
        yield ("Result tree file", self.output_result_tree_path)
        yield ("Total time", self.total_time)
