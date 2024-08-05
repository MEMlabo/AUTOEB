from typing import TYPE_CHECKING, overload

from .not_supported_error import NotSupportedError
from .tree_format_error import TreeFormatError
from .node import Node
from .tree import Tree
if TYPE_CHECKING:
    from .io.iohandler import TreeIOHandler
    from typing import TextIO


@overload
def read_tree(source: str, tree_type: "TreeIOHandler") -> Tree:
    """系統樹を読み込みます。

    Args:
        source (str): 読み込むファイルパス
        tree_type (TreeIOHandler): 使用するTreeIOHandlerのインスタンス

    Raise:
        TreeFormatError: ツリーのフォーマットが無効

    Returns:
        Tree: 読み込んだツリー
    """
    ...


@overload
def read_tree(source: "TextIO", tree_type: "TreeIOHandler") -> Tree:
    """系統樹を読み込みます。

    Args:
        source (TextIO): 読み込むストリーム
        tree_type (TreeIOHandler): 使用するTreeIOHandlerのインスタンス

    Raise:
        TreeFormatError: ツリーのフォーマットが無効

    Returns:
        Tree: 読み込んだツリー
    """
    ...


def read_tree(source: "str | TextIO", tree_type: "TreeIOHandler") -> Tree:
    """系統樹を読み込みます。

    Args:
        source (str | TextIO): 読み込むファイルパスまたはストリーム
        tree_type (TreeIOHandler): 使用するTreeIOHandlerのインスタンス

    Raise:
        TreeFormatError: ツリーのフォーマットが無効

    Returns:
        Tree: 読み込んだツリー
    """
    if isinstance(source, str):
        with open(source, 'r') as stream:
            return tree_type.read_tree(stream)
    else:
        return tree_type.read_tree(source)
