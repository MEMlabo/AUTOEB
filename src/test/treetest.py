from io import StringIO
import unittest
from autoeb.nnigen import read_tree, Node, Tree
from autoeb.nnigen.io import treetype

from test.common import get_output_dir, get_test_data_dir


class TreeTest(unittest.TestCase):
    """系統樹オブジェクトのユニットテストを行うクラスです。
    """

    @classmethod
    def __verify_node(cls, node: Node | None, name: str, length: float | None) -> Node:
        """Nodeインスタンスの状態を検証します。

        Args:
            node (Node | None): 検証を行うNodeのインスタンス
            name (str): ラベル
            length (float | None): 枝長

        Returns:
            Node: 検証後のNodeインスタンス
        """
        assert node is not None
        assert node.name == name
        if length is None:
            assert node.length is None
        else:
            assert node.length == length
        return node

    def test_load_newick(self) -> None:
        """newickフォーマットの読み込みをテストします。
        """
        tree: Tree = read_tree(get_test_data_dir() + "newick-7.tree", treetype.newick)

        root: Node = self.__verify_node(tree.root, "100/100", 0.2)
        self.__verify_node(root.next1, "1", 0.1)
        node21: Node = self.__verify_node(root.next3, "98/97", 0.3)
        self.__verify_node(node21.next3, "211", 0.4)
        self.__verify_node(node21.next4, "212", 0.4)
        node22: Node = self.__verify_node(root.next4, "95/100", 0.1)
        node221: Node = self.__verify_node(node22.next3, "50/75", 0.2)
        self.__verify_node(node221.next3, "2211", 0.1)
        self.__verify_node(node221.next4, "2212", 0.1)
        self.__verify_node(root.next2, "3", 0.1)

    def test_save_newick(self) -> None:
        """newickフォーマットの出力をテストします。
        """
        root = Node("100", 0.2)
        node1 = Node("A", 0.1, root)
        node2 = Node("B", 0.2, root)
        root.next1 = node1
        root.next2 = node2
        node1.next2 = node2
        node2.next2 = node1
        node3 = Node("C", 0.1, root)
        node4 = Node("D", 0.15, root)
        root.next3 = node3
        root.next4 = node4
        node3.next2 = node3
        node4.next2 = node4
        tree = Tree(root)

        tree_text: str
        with StringIO() as io:
            tree.export(io, treetype.newick)
            tree_text = io.getvalue()

        assert tree_text == "(A:0.1,(C:0.1,D:0.15)100:0.2,B:0.2);"

    def test_nni(self) -> None:
        """NNI生成のテストを行います。
        """
        tree: Tree = read_tree(get_test_data_dir() + "newick-4.tree", treetype.newick)
        predict = [
            "(A:0.1,(B:0.3,C:0.1)100/100:0.2,D:0.1);",
            "(A,(D,C),B);",
            "(A,(B,D),C);"
        ]
        predict.sort()
        actual: list[str] = [None] * len(predict)  # type:ignore
        index = 0
        for current in tree.iterate_all_nni_trees():
            with StringIO() as io:
                current.export(io, treetype.newick)
                actual[index] = io.getvalue()
                index += 1
        assert predict[-1] is not None

        actual.sort()
        for i in range(len(actual)):
            assert predict[i] == actual[i]
