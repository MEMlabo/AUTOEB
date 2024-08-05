from abc import abstractmethod
from typing import TextIO

from ..tree import Tree


class TreeIOHandler:

    """系統樹の入出力を扱うクラスです。
    """

    def __init__(self) -> None:
        """TreeIOHandlerの新しいインスタンスを初期化します。
        """
        pass

    @abstractmethod
    def read_tree(self, stream: TextIO) -> Tree:
        """系統樹を読み込みます。

        Args:
            stream (TextIO): 読み込む系統樹のストリーム

        Raises:
            TreeFormatError: textのフォーマットが無効

        Returns:
            Tree: 読み込んだ系統樹に基づくTreeのインスタンス
        """
        raise NotImplementedError()

    @abstractmethod
    def write_tree(self, stream: TextIO, tree: Tree) -> None:
        """系統樹を出力します。

        Args:
            stream (TextIO): 出力先
            tree (Tree): 出力する系統樹
        """
        raise NotImplementedError()
