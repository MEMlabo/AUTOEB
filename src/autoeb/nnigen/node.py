from copy import deepcopy
from typing import Generator, Tuple


class Node:
    """系統樹の枝を表すクラスです。
    """

    def __init__(
        self,
        name: str,
        length: float | None,
        next1: "Node | None" = None,
        next2: "Node | None" = None,
        next3: "Node | None" = None,
        next4: "Node | None" = None
    ) -> None:
        """Nodeの新しいインスタンスを初期化します。

        Args:
            name (str): 名前
            length (float | None): 枝長
            next1 (Node | None, optional): 隣接する枝1. Defaults to None.
            next2 (Node | None, optional): 隣接する枝2. Defaults to None.
            next3 (Node | None, optional): 隣接する枝3. Defaults to None.
            next4 (Node | None, optional): 隣接する枝4. Defaults to None.
        """
        self.__name: str = name
        self.__length: float | None = length

        # Conversion from rooted format
        #
        # next1--+        +--next3-|
        #        |-(self)-|
        # next2--+        +--next4-|
        #
        #
        #          +--next2
        # --next1--|         +--next3
        #          +--(self)-|
        #                    +--next4
        self.__next1: Node | None = next1
        self.__next2: Node | None = next2
        self.__next3: Node | None = next3
        self.__next4: Node | None = next4

    @property
    def name(self) -> str:
        """ラベル名を取得します。
        """
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        """ラベル名を設定します。
        """
        self.__name = value

    @property
    def length(self) -> float | None:
        """枝長を取得します。
        """
        return self.__length

    @length.setter
    def length(self, value: float | None) -> None:
        """枝長を設定します。
        """
        self.__length = value

    @property
    def next1(self) -> "Node | None":
        """隣接するノードを取得します。
        rooted treeでは親ノードを表します。
        """
        return self.__next1

    @next1.setter
    def next1(self, value: "Node | None") -> None:
        """隣接するノードを設定します。
        rooted treeでは親ノードを表します。
        """
        self.__next1 = value

    @property
    def next2(self) -> "Node | None":
        """隣接するノードを取得します。
        rooted treeでは姉妹ノードを表します。
        """
        return self.__next2

    @next2.setter
    def next2(self, value: "Node | None") -> None:
        """隣接するノードを設定します。
        rooted treeでは姉妹ノードを表します。
        """
        self.__next2 = value

    @property
    def next3(self) -> "Node | None":
        """隣接するノードを取得します。
        rooted treeでは子ノードを表します。
        """
        return self.__next3

    @next3.setter
    def next3(self, value: "Node | None") -> None:
        """隣接するノードを設定します。
        rooted treeでは子ノードを表します。
        """
        self.__next3 = value

    @property
    def next4(self) -> "Node | None":
        """隣接するノードを取得します。
        rooted treeでは子ノードを表します。
        """
        return self.__next4

    @next4.setter
    def next4(self, value: "Node | None") -> None:
        """隣接するノードを設定します。
        rooted treeでは子ノードを表します。
        """
        self.__next4 = value

    @property
    def is_leaf(self) -> bool:
        """インスタンスが葉を表すかどうかを取得します。
        """
        return not (self.next1 and self.next2 and self.next3 and self.next4)

    @property
    def is_root(self) -> bool:
        """自身が値を表すかどうかを取得します。
        """
        return self.find_root() == self

    def __iterate_all_next(self) -> "Generator[Node, None, None]":
        """全ての隣接ノードを列挙します。

        Yields:
            Generator[Node, None, None]: 隣接ノードを列挙するGeneratorのインスタンス
        """
        if self.__next1:
            yield self.__next1
        if self.__next2:
            yield self.__next2
        if self.__next3:
            yield self.__next3
        if self.__next4:
            yield self.__next4

    def get_next_nodes(self) -> "list[Node]":
        """隣接するノードのリストを取得します。

        Returns:
            list[Node]: 各ノード（サイズ: 0-4）
        """

        return list(self.__iterate_all_next())

    @classmethod
    def __iterate_next(cls, node: "Node", exc: "Node") -> "Generator[Node, None, None]":
        """指定したノード以外の全隣接ノードを列挙します。

        Args:
            node (Node): 隣接ノードを取得したいノード
            exc (Node): 除外ノード

        Yields:
            Generator[Node, None, None]: excを除くnodeにおける全ての隣接ノードを列挙するGeneratorのインスタンス
        """
        # 子要素をリターン
        if (node.next1 == exc or node.next2 == exc) and node.next3 and node.next4:
            yield node.next3
            for descendant in cls.__iterate_next(node.next3, node):
                yield descendant
            yield node.next4
            for descendant in cls.__iterate_next(node.next4, node):
                yield descendant
        if (node.next3 == exc or node.next4 == exc) and node.next1 and node.next2:
            yield node.next1
            for descendant in cls.__iterate_next(node.next1, node):
                yield descendant
            yield node.next2
            for descendant in cls.__iterate_next(node.next2, node):
                yield descendant

    def iterate_all_nodes(self) -> "Generator[Node, None, None]":
        """自身を含む全ノードを列挙します。

        Yields:
            Generator[Node, None, None]: 自身を含む全ノードを列挙するGeneratorのインスタンス
        """

        # 自身を最初にリターン
        yield self
        for child in self.get_next_nodes():
            # 次に子要素をリターン
            yield child
            # 孫要素以下を列挙
            for descendant in Node.__iterate_next(child, self):
                yield descendant

    def find_root(self) -> "Node":
        """ルートとなるNodeのインスタンスを取得します。

        Returns:
            Node: ルートとなるNodeのインスタンス
        """
        current: Node = self
        while True:
            next1: Node | None = current.next1
            if next1 is None:
                raise ValueError("Invalid tree state")
            if next1.next1 == current:
                return current
            current = next1

    def clear_length(self) -> None:
        """子ノード含む全てのノードの枝長を削除します。
        """
        for current in self.iterate_all_nodes():
            current.length = None

    def clear_bp_label(self) -> None:
        """葉以外のノードの名前を削除します。
        """
        for current in self.iterate_all_nodes():
            if not current.is_leaf:
                current.name = ""

    def get_nni(self) -> "Tuple[Node, Node, Node]":
        """3つのNNIノードを取得します。

        Raises:
            ValueError: 葉を表すインスタンスに対してこのメソッドが呼び出された

        Returns:
            Tuple[Node, Node, Node]: 三つのNNI樹形。一つ目はselfと同値，二つ目はnext2とnext3を交換したもの，三つめはnext2とnext4を交換した者もの
        """
        if self.is_leaf:
            raise ValueError("NNI operation cannot process leaf")

        # SOURCE
        #        +-next2
        # -next1-|       +-next3
        #        +-self--|
        #                +-next4
        # RETURNS
        # result1: equals to self
        #        +-next2
        # -next1-|         +-next3
        #        +-result1-|
        #                  +-next4
        # result2: next2 and next3 are exchanged
        #        +-next3
        # -next1-|         +-next2
        #        +-result2-|
        #                  +-next4
        # result3: next2 and next4 are exchanged
        #        +-next4
        # -next1-|         +-next3
        #        +-result3-|
        #                  +-next2
        result1 = deepcopy(self)

        result2 = deepcopy(self)
        result2_next1: Node = result2.next1  # type:ignore
        result2_next2: Node = result2.next2  # type:ignore
        result2_next3: Node = result2.next3  # type:ignore
        result2_next4: Node = result2.next4  # type:ignore
        if self.is_root:
            result2.next3 = result2_next2
            result2.next2 = result2_next3
            result2_next1.next2 = result2_next3
            result2_next3.next2 = result2_next1
            result2_next2.next2 = result2_next4
            result2_next4.next2 = result2_next2
        else:
            result2.next3 = result2_next2
            result2.next2 = result2_next3
            if result2_next1.next3 == result2:
                result2_next1.next4 = result2_next3
            elif result2_next1.next4 == result2:
                result2_next1.next3 = result2_next3
            elif result2_next1.next1 == result2:
                result2_next1.next2 = result2_next3
            else:  # result2_next1.next2 == result2
                result2_next1.next1 = result2
            result2_next3.next1 = result2_next1
            result2_next3.next2 = result2
            result2_next2.next1 = result2
            result2_next2.next2 = result2_next4
            result2_next4.next2 = result2_next2

        result3 = deepcopy(self)
        result3_next1: Node = result3.next1  # type:ignore
        result3_next2: Node = result3.next2  # type:ignore
        result3_next3: Node = result3.next3  # type:ignore
        result3_next4: Node = result3.next4  # type:ignore
        if self.is_root:
            result3.next4 = result3_next2
            result3.next2 = result3_next4
            result3_next1.next2 = result3_next4
            result3_next4.next2 = result3_next1
            result3_next2.next2 = result3_next3
            result3_next3.next2 = result3_next2
        else:
            result3.next4 = result3_next2
            result3.next2 = result3_next4
            if result3_next1.next3 == result3:
                result3_next1.next4 = result3_next4
            elif result3_next1.next4 == result3:
                result3_next1.next3 = result3_next4
            elif result3_next1.next1 == result3:
                result3_next1.next2 = result3_next4
            else:  # result3_next1.next2 == result3
                result3_next1.next1 = result3_next4
            result3_next4.next1 = result3_next1
            result3_next4.next2 = result3
            result3_next3.next2 = result3_next2
            result3_next2.next1 = result3
            result3_next2.next2 = result3_next3

        result2.clear_length()
        result2.clear_bp_label()
        result3.clear_length()
        result3.clear_bp_label()

        return (result1, result2, result3)

    def __str__(self) -> str:
        """文字列に変換します。

        Returns:
            str: 変換後の文字列
        """
        return f"{self.name}: {self.length}"
