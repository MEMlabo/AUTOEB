from typing import TYPE_CHECKING, Generator, TextIO, Tuple, overload


from .node import Node
if TYPE_CHECKING:
    from .io.iohandler import TreeIOHandler


class Tree:
    """系統樹を表します。
    """

    def __init__(self, root: Node) -> None:
        """Treeの新しいインスタンスを初期化します。

        Args:
            root (Node): ルート
        """
        self.__root: Node = root

    @property
    def root(self) -> Node:
        """ルートとなるノードを取得します。
        """
        return self.__root

    def iterate_all_leaves(self) -> Generator[Node, None, None]:
        """葉となるNodeを全て列挙します。

        Yields:
            Generator[Node, None, None]: 葉となるNodeを全て列挙するGeneratorのインスタンス
        """
        for current in self.root.iterate_all_nodes():
            if current.is_leaf:
                yield current

    def iterate_all_branches(self) -> Generator[Node, None, None]:
        """枝となるNodeを全て列挙します。

        Yields:
            Generator[Node, None, None]: 枝となるNodeを全て列挙するGeneratorのインスタンス
        """
        for current in self.root.iterate_all_nodes():
            if not current.is_leaf:
                yield current

    def iterate_all_nni_trees(self) -> "Generator[Tree, None, None]":
        """全てのNNI樹形を列挙します。

        Yields:
            Generator[Tree, None, None]: 全てのNNI樹形を列挙するGeneratorのインスタンス。最初にselfと同樹形のツリーが列挙される
        """
        generator: Generator[Node, None, None] = self.iterate_all_branches()
        root: Node = next(generator)
        root_nni: Tuple[Node, Node, Node] = root.get_nni()
        yield Tree(root_nni[0])
        yield Tree(root_nni[1])
        yield Tree(root_nni[2])
        for current in generator:
            nni: Tuple[Node, Node, Node] = current.get_nni()
            yield Tree(nni[1].find_root())
            yield Tree(nni[2].find_root())

    @overload
    def export(self, destination: str, tree_type: "TreeIOHandler") -> None:
        """系統樹のエクスポートを行います。

        Args:
            destination (str): 出力先のファイルパス
            tree_type (TreeIOHandler): 系統樹のタイプ
        """
        ...

    @overload
    def export(self, destination: TextIO, tree_type: "TreeIOHandler") -> None:
        """系統樹のエクスポートを行います。

        Args:
            destination (TextIO): 出力先のストリーム
            tree_type (TreeIOHandler): 系統樹のタイプ
        """
        ...

    def export(self, destination: str | TextIO, tree_type: "TreeIOHandler") -> None:
        """系統樹のエクスポートを行います。

        Args:
            destination (str | TextIO): 出力先のファイルパスまたはストリーム
            tree_type (TreeIOHandler): 系統樹のタイプ
        """
        if isinstance(destination, str):
            with open(destination, "wt") as stream:
                tree_type.write_tree(stream, self)
        else:
            tree_type.write_tree(destination, self)
