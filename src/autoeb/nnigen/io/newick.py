from typing import Generator, TextIO

from ..not_supported_error import NotSupportedError
from .iohandler import TreeIOHandler
from .stringhelper import _StringHelper
from ..tree_format_error import TreeFormatError
from ..node import Node
from ..tree import Tree


class NewickIOHandler(TreeIOHandler):
    """newickフォーマットの系統樹のI/Oを扱います。
    """

    def __init__(self) -> None:
        """NewickIOHandlerの新しいインスタンスを初期化します。
        """
        pass

    def read_tree(self, stream: TextIO) -> Tree:
        src_text: str = stream.readline()
        end_index: int = src_text.index(';')
        root: Node = NewickIOHandler.__read_tree_internal(src_text[:end_index])
        return Tree(root)

    @staticmethod
    def __split_elements(text: str) -> list[str]:
        """newickフォーマット内の要素を分割します。

        Args:
            text (str): newick文字列

        Returns:
            list[str]: 各枝の要素
        """
        def inner(text: str) -> Generator[str, None, None]:
            level: int = -1
            index: int = -1
            start: int = 1
            for char in text:
                index += 1
                if char == '(':
                    level += 1
                    continue
                if char == ')':
                    level -= 1
                    continue
                if char == ',' and level == 0:
                    yield text[start:index]
                    start = index + 1
            if start <= index - 1:
                yield text[start:-1]

        return list[str](inner(text))

    @staticmethod
    def __get_element_info(text: str) -> tuple[str, float | None, str | None]:
        """ノードの情報を取得します。

        Args:
            text (str): 読み込む文字列

        Returns:
            tuple[str, float | None, str | None]: ノード名，枝長，子ノードのnewick文字列
        """
        coron_index: int
        parentheses_index: int
        try:
            coron_index = _StringHelper.last_index(text, ':')
        except ValueError:
            coron_index = -1
        try:
            parentheses_index = _StringHelper.last_index(text, ')')
        except ValueError:
            parentheses_index = -1

        # +length
        if coron_index != -1:
            node_length = float(text[coron_index + 1:])
            node_left: str = text[:coron_index]
            # +length, +child
            if parentheses_index != -1:
                return (node_left[parentheses_index + 1:], node_length, node_left[:parentheses_index + 1])
            # +length, -child
            return (node_left, node_length, None)
        # -length, +child
        if parentheses_index != -1:
            return (text[parentheses_index + 1:], None, text[:parentheses_index + 1])
        # -length, -child
        return (text, None, None)

    @classmethod
    def __read_tree_internal(cls, text: str) -> Node:
        """系統樹を読み込みます。

        Args:
            text (str): newick文字列

        Raises:
            TreeFormatError: textのフォーマットが無効

        Returns:
            Node: 読み込んだNodeのインスタンス
        """
        if text.count('(') != text.count(')'):
            raise TreeFormatError()
        elements: list[str] = cls.__split_elements(text)
        return cls.__create_node(elements, None)

    @classmethod
    def __create_node(cls, elements: list[str], parent: Node | None) -> Node:
        """ノードを生成します。

        Args:
            elements (list[str]): ノードを表す文字列
            parent (Node | None): 親ノード

        Returns:
            Node: parentがNoneの場合，rootとなるノード。それ以外でparent
        """
        length: int = len(elements)
        if length == 0:
            raise ValueError("No element is given")

        if parent:
            if length < 2:
                raise TreeFormatError()
            if length > 2:
                # TODO: Implement operation when len(children) > 2
                raise NotSupportedError("Polytomy tree is not supported yet")
            next3_info: tuple[str, float | None, str | None] = cls.__get_element_info(elements[0])
            next3 = Node(next3_info[0], next3_info[1], next1=parent)
            parent.next3 = next3
            if next3_info[2]:
                next3_children = cls.__split_elements(next3_info[2])
                cls.__create_node(next3_children, next3)

            next4_info: tuple[str, float | None, str | None] = cls.__get_element_info(elements[1])
            next4 = Node(next4_info[0], next4_info[1], next1=parent)
            parent.next4 = next4
            if next4_info[2]:
                next4_children = cls.__split_elements(next4_info[2])
                cls.__create_node(next4_children, next4)

            next3.next2 = next4
            next4.next2 = next3

            return parent
        # If parent is None, this method returns the Node instance which represents ROOT.
        else:
            if length < 3:
                raise ValueError("The amount of Node must be larger than or equal to 3")
            split_elements: list[tuple[str, float | None, str | None]]
            split_elements = [None] * length  # type: ignore
            for i in range(length):
                split_elements[i] = cls.__get_element_info(elements[i])
            index_has_child: int = 0
            for current in split_elements:
                if current[2] is not None:
                    break
                index_has_child += 1
            if index_has_child == 3:
                raise TreeFormatError()
            result_info: tuple[str, float | None, str | None] = split_elements.pop(index_has_child)
            result = Node(result_info[0], result_info[1])
            next1 = Node(split_elements[0][0], split_elements[0][1], next1=result)
            next2 = Node(split_elements[1][0], split_elements[1][1], next1=result)
            if len(split_elements) > 2:
                # TODO: Implement operation when len(split_elements) > 2
                raise NotSupportedError("Polytomy tree is not supported yet")

            result.next1 = next1
            result.next2 = next2

            next1.next2 = next2
            next2.next2 = next1

            if split_elements[0][2]:
                cls.__create_node(cls.__split_elements(split_elements[0][2]), next1)
            if split_elements[1][2]:
                cls.__create_node(cls.__split_elements(split_elements[1][2]), next2)

            # result_info[2] is never None
            child_text: str = result_info[2]  # type:ignore
            children: list[str] = cls.__split_elements(child_text)

            cls.__create_node(children, result)
            return result

    @classmethod
    def __write_node(cls, stream: TextIO, node: Node) -> None:
        """newick形式でノードを出力します。

        Args:
            stream (TextIO): 出力先ストリーム
            node (Node): 出力するノード
        """
        # has child
        if not node.is_leaf:
            stream.write('(')
            next3: Node = node.next3  # type:ignore
            next4: Node = node.next4  # type:ignore
            cls.__write_node(stream, next3)
            stream.write(',')
            cls.__write_node(stream, next4)
            stream.write(')')
        length_text: str = f":{node.length}" if node.length is not None else ""
        stream.write(node.name + length_text)

    def write_tree(self, stream: TextIO, tree: Tree) -> None:
        root: Node = tree.root
        stream.write('(')
        next1: Node = root.next1  # type:ignore
        next2: Node = root.next2  # type:ignore
        self.__write_node(stream, next1)
        stream.write(',')
        self.__write_node(stream, tree.root)
        stream.write(',')
        self.__write_node(stream, next2)
        stream.write(");")
