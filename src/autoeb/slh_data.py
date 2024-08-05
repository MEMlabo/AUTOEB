from copy import deepcopy
from io import TextIOBase
import regex
from typing import Generator, Iterable, Iterator, overload


class SlhData:
    """SITELHファイルのデータを格納します。
    """

    @property
    def tree_count(self) -> int:
        """ツリー数を取得します。
        """
        return len(self.__values)

    @property
    def site_count(self) -> int:
        """座位数を取得します。

        Raises:
            ValueError: 現在のインスタンスに要素が格納されていない
        """
        if len(self.__values) == 0:
            raise ValueError("current instance doesn't have any elements")
        return len(self.__values[0])

    def __init__(self, values: Iterable[list[float]] | None = None) -> None:
        """SlhDataの新しいインスタンスを初期化します。

        Args:
            values (Iterable[list[float]] | None): 含めるデータ
        """
        if values is None:
            self.__values: list[list[float]] = []
            return
        self.__values = list[list[float]](values)

    @overload
    def __getitem__(self, index: int) -> list[float]:
        ...

    @overload
    def __getitem__(self, index: slice) -> "SlhData":
        ...

    def __getitem__(self, index: int | slice) -> "list[float] | SlhData":
        """指定したインデックスまたは範囲を取得します。

        Args:
            index (int | slice): インデックスまたは範囲

        Returns:
            list[float] | SlhData: 指定したインデックスまたは範囲の要素
        """
        if isinstance(index, int):
            return self.__values[index]
        result = SlhData()
        result.__values = self.__values[index]
        return result

    @classmethod
    def concat(cls, left: "SlhData", right: "SlhData") -> "SlhData":
        """2つのデータを結合し，新たなインスタンスを返します。

        Args:
            left (SlhData): 結合するデータ1
            right (SlhData): 結合するデータ2

        Returns:
            SlhData: 結合後のデータ

        Raises:
            ValueError: 現在のインスタンスとotherのインスタンスの座位数が異なる
        """
        result: SlhData = deepcopy(left)
        result.merge(right)
        return result

    @overload
    @classmethod
    def load(cls, source: str) -> "SlhData":
        """SITELHファイルを読み込みます。

        Args:
            source (str): 読み込むSITELHファイルのパス

        Raises:
            ValueError: SITELHファイルのフォーマットが無効

        Returns:
            SlhData: sourceを読み込んで生成されたSlhDataの新しいインスタンス
        """
        ...

    @overload
    @classmethod
    def load(cls, source: TextIOBase) -> "SlhData":
        """SITELHファイルを読み込みます。

        Args:
            source (TextIOBase): 読み込むSITELHファイルのストリームオブジェクト

        Raises:
            ValueError: SITELHファイルのフォーマットが無効

        Returns:
            SlhData: sourceを読み込んで生成されたSlhDataの新しいインスタンス
        """
        ...

    @classmethod
    def load(cls, source: str | TextIOBase) -> "SlhData":
        if isinstance(source, str):
            with open(source, "rt") as io:
                return cls.load(io)
        line: str = source.readline()
        if line == "":
            raise ValueError("Invalid SITELH file format")
        tree_count: int
        site_count: int
        try:
            spl: list[str] = line.split(' ')
            tree_count = int(spl[0])
            site_count = int(spl[1])
        except:
            raise ValueError("Invalid SITELH file format")

        line = source.readline()
        result = cls()
        while line != "":
            if line == "\n":
                continue
            line = line.strip()
            values: list[str] = regex.split(r"\s+", line)
            if len(values) - 1 != site_count:
                raise ValueError("Invalid SITELH file format")
            result.__append([float(f) for f in values[1:]])
            line = source.readline()
        if result.tree_count != tree_count:
            raise ValueError("Invalid SITELH file format")

        return result

    def __append(self, values: list[float]) -> None:
        """データを追加します。

        Args:
            values (list[float]): 追加する尤度一覧
        """
        self.__values.append(values)

    def itearte_values(self) -> Generator[Iterator[float], None, None]:
        """各ツリーにおける値を列挙します。

        Yields:
            Generator[Iterator[float], None, None]: ツリーの尤度のイテレータを列挙するインスタンス
        """
        for current in self.__values:
            yield iter(current)

    def merge(self, other: "SlhData") -> None:
        """データを結合します。

        Args:
            other (SlhData): 結合するデータ

        Raises:
            ValueError: 現在のインスタンスとotherのインスタンスの座位数が異なる
        """
        if other.tree_count == 0:
            return
        if self.tree_count == 0:
            self.__values = deepcopy(other.__values)
        else:
            if self.site_count != other.site_count:
                raise ValueError("site_count is differ between 2 instances")
            self.__values.extend(other.__values)

    @overload
    def export(self, destination: str) -> None:
        """SITELHファイルへの出力を行います。

        Args:
            destination (str): 出力先のパス
        """
        ...

    @overload
    def export(self, destination: TextIOBase) -> None:
        """SITELHファイルへの出力を行います。

        Args:
            destination (TextIOBase): 出力先のストリームオブジェクト
        """
        ...

    def export(self, destination: str | TextIOBase) -> None:
        if isinstance(destination, str):
            with open(destination, "wt") as io:
                return self.export(io)

        def writeline(io: TextIOBase, text: str) -> None:
            print(text, file=io)

        writeline(destination, f"{self.tree_count} {self.site_count}")
        if self.tree_count == 1:
            destination.write(f"Site_Lh    {self.__values[0][0]}")
            for current_lh in self.__values[0][1:]:
                destination.write(" " + str(current_lh))
            writeline(destination, "")
        else:
            index = 1
            for current_tree in self.__values:
                if len(current_tree) == 0:
                    continue
                destination.write(f"Tree{index}    {current_tree[0]}")
                for current_lh in current_tree[1:]:
                    destination.write(" " + str(current_lh))
                writeline(destination, "")
                index += 1

    def __add__(self, other: "SlhData") -> "SlhData":
        return SlhData.concat(self, other)
