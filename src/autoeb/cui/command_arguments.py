from argparse import ArgumentError, ArgumentParser, Namespace
import os

from ..nnigen.io import TreeIOHandler, treetype
from ..value_range import ValueRange


class CommandArguments:
    """コマンド引数を表すクラスです。
    """

    __parser: ArgumentParser | None = None

    def __init__(self, args: list[str]) -> None:
        """CommandArgumentsの新しいインスタンスを初期化します。

        Args:
            args (list[str]): コマンド引数
        """
        self.__namespace: Namespace = self.get_arg_parser().parse_args(args)

    @property
    def seq_file(self) -> str:
        """配列ファイルのパスを取得します。
        """
        result: str = self.__namespace.seq
        if not os.path.isfile(result):
            raise ArgumentError(None, f"sequence file '{result}' does not exists")
        return os.path.abspath(result)

    @property
    def tree_file(self) -> str:
        """ツリーファイルのパスを取得します。
        """
        result: str = self.__namespace.tree
        if not os.path.isfile(result):
            raise ArgumentError(None, f"tree file '{result}' does not exists")
        return os.path.abspath(result)

    @property
    def model(self) -> str:
        """進化モデルを取得します。
        """
        return self.__namespace.model

    @property
    def rell_boot(self) -> int:
        """RELL bootstrapの複製数を取得します。
        """
        result: int = self.__namespace.bootstrap
        if result < 1000:
            raise ArgumentError(None, "value must be greater or equal to 1000")
        return result

    @property
    def seed(self) -> int:
        """RELL-bootのシード値を取得します。
        """
        result: int = self.__namespace.seed
        if result < -1:
            raise ArgumentError(None, "value must be greater or equal to -1")
        return result

    @property
    def out_dir(self) -> str:
        """出力先ディレクトリを取得します。
        """
        result: str = self.__namespace.out
        if not os.path.isdir(result):
            os.mkdir(result)
        return os.path.abspath(result)

    @property
    def bipartition_range(self) -> ValueRange:
        """解析を行う枝の範囲を取得します。
        """
        return ValueRange.parse(self.__namespace.range)

    @property
    def sig_level(self) -> float:
        """有意水準を取得します。
        """
        result: float = self.__namespace.sig_level
        if result < 0 or 1 < result:
            raise ArgumentError(None, "value must be within the range 0 to 1")
        return result

    @property
    def tree_type(self) -> TreeIOHandler:
        """系統樹ファイルの種類を取得します。
        """
        # TODO: Implement switching tree type
        return treetype.newick

    @property
    def threads(self) -> int:
        """スレッド数を取得します。
        """
        result: int = self.__namespace.thread
        if result < 1:
            raise ArgumentError(None, "value must be greater or equal to 1")
        return result

    @property
    def out_format(self) -> str:
        """出力フォーマットを取得します。
        """
        return self.__namespace.out_format

    @property
    def iqtree_params(self) -> str | None:
        """IQ-TREEに与えるパラメータを取得します。
        """
        result: str | None = self.__namespace.iqtree_param
        if not (result is None) and not os.path.isfile(result):
            raise ArgumentError(None, f"text file '{result}' does not exist")
        return result

    @property
    def iqtree_verbose(self) -> bool:
        """IQ-TREEのログを全て出力するかどうかを取得します。
        """
        return self.__namespace.iqtree_verbose

    @property
    def output_tmp_files(self) -> bool:
        """中間ファイルを残すかどうかを取得します。
        """
        return self.__namespace.output_tmp_files

    @property
    def redo(self) -> bool:
        """チェックポイントを無視して再解析を行うかどうかを取得します。
        """
        return self.__namespace.redo

    @classmethod
    def get_arg_parser(cls) -> ArgumentParser:
        """使用するArgumentParserのインスタンスを取得します。

        Returns:
            ArgumentParser: 使用するArgumentParserのインスタンス
        """
        if not cls.__parser:
            result = ArgumentParser(prog="AUTOEB", description="Execute AU-Test for each nodes")
            cls.__parser = result
            cls.__add_options(result)
        return cls.__parser

    @staticmethod
    def __add_options(parser: ArgumentParser) -> None:
        """オプションの設定を行います。

        Args:
            parser (ArgumentParser): 設定を行うArgumentParserのインスタンス
        """
        from . import __version__
        parser.add_argument("-v", "--version", action="version", help="display the version", version=__version__)
        parser.add_argument("-s", "--seq", type=str, required=True, help="sequence file", metavar="FILE")
        parser.add_argument("-t", "--tree", type=str, required=True, help="ML-tree file", metavar="FILE")
        parser.add_argument("-m", "--model", type=str, required=True, help="substitution model", metavar="MODEL")
        parser.add_argument("--iqtree-param", default=None, type=str, help="IQ-TREE parameter arguments (default is empty string)", metavar="PARAM")
        parser.add_argument("--range", default="ALL", type=str, help="the range: which branch to be analyzed. e.g.'ALL', '3-10', '2,3,10-20', '5-', '-20' (default=ALL)", metavar="RANGE")
        parser.add_argument("--sig-level", default=0.05, type=float, help="the significance level (0-1, default=0.05)", metavar="FLOAT")
        parser.add_argument("-b", "--bootstrap", default=10_0000, type=int, help="replicates of RELL bootstrap (>=1000, default=100,000)", metavar="INT")
        parser.add_argument("--seed", default=-1, type=int, help="seed of random value (>= -1). if larger than 0, specified value is used for seed (default=-1)", metavar="INT")
        parser.add_argument("-o", "--out", type=str, required=True, help="destination folder", metavar="DIR")
        parser.add_argument("-f", "--out-format", default='{src}/{bin}', type=str, help="format of branch name (default='{src}/{bin}')", metavar="STR")
        parser.add_argument("-T", "--thread", default=1, type=int, help="numbmer of threads IQ-TREE uses (default=1)", metavar="INT")
        parser.add_argument("--iqtree-verbose", action="store_true", help="redirect IQ-TREE stdout")
        parser.add_argument("--output-tmp-files", action="store_true", help="output files IQ-TREE and CONSEL generated")
        parser.add_argument("--redo", action="store_true", help="Ignore checkpoints and redo the analysis")

    def get_out_file_path(self, filename: str) -> str:
        """出力ファイルパスを取得します。

        Args:
            filename (str): ファイル名

        Returns:
            str: out_dirを反映したファイルのパス
        """
        return os.path.join(self.out_dir, filename)
