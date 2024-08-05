from typing import Generator


class _Point:
    """ValueRangeのうち，特定の一つの値を表します。
    """
    @property
    def value(self) -> int:
        """値を取得します。
        """
        return self.__value

    def __init__(self, value: int) -> None:
        """_Pointの新しいインスタンスを初期化します。

        Args:
            value (int): 設定する値
        """
        self.__value: int = value

    @classmethod
    def parse(cls, value: str) -> "_Point":
        """文字列から_Pointの新しいインスタンスを生成します。

        Args:
            value (str): 文字列

        Returns:
            _Point: valueから生成された新しいインスタンス
        """
        return cls(int(value))

    def __compare_to(self, value: "int | _Point") -> int:
        """指定した値を大小を比較します。

        Args:
            value (int | _Point): 比較対象

        Raises:
            TypeError: valueが無効な型

        Returns:
            int: self < valueで負の値，self == valueで0，self > valueで正の値
        """
        if isinstance(value, int):
            return self.value - value
        if isinstance(value, _Point):
            return self.value - value.value
        raise TypeError()

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, _Point):
            return self.value == __value.value
        if isinstance(__value, int):
            return self.value == __value
        return False

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __lt__(self, __value: "int | _Point") -> bool:
        return self.__compare_to(__value) < 0

    def __le__(self, __value: "int | _Point") -> bool:
        return self.__compare_to(__value) <= 0

    def __gt__(self, __value: "int | _Point") -> bool:
        return self.__compare_to(__value) > 0

    def __ge__(self, __value: "int | _Point") -> bool:
        return self.__compare_to(__value) >= 0

    def __str__(self) -> str:
        return str(self.value)


class _Range:
    """ValueRangeのうち，特定の値の範囲を表します。
    """

    @property
    def start(self) -> int | None:
        """開始値を取得します。
        """
        return None if self.__start == -1 else self.__start

    @property
    def end(self) -> int | None:
        """終了値を取得します。
        """
        return None if self.__end == -1 else self.__end

    def __init__(self, start: int | None, end: int | None) -> None:
        """_Rangeの新しいインスタンスを初期化します。

        Args:
            start (int | None): 開始値
            end (int | None): 終了値
        """
        self.__start: int = -1 if start is None else start
        self.__end: int = -1 if end is None else end

    @classmethod
    def parse(cls, value: str) -> "_Range":
        """文字列から_Rangeの新しいインスタンスを生成します。

        Args:
            value (str): 文字列

        Returns:
            _Range: valueから生成された新しいインスタンス
        """
        from .nnigen.io.stringhelper import _StringHelper
        separator_index: int = value.find('-')
        if separator_index != _StringHelper.last_index(value, '-'):
            raise ValueError(f"文字列'{value}'を変換できません")
        start: int | None = None if separator_index == 0 else int(value[:separator_index])
        end: int | None = None if separator_index == len(value) - 1 else int(value[separator_index + 1:])
        return cls(start, end)

    def __compare_to(self, value: "_Range") -> int:
        """指定した値を大小を比較します。

        Args:
            value (_Range): 比較対象

        Raises:
            TypeError: valueが無効な型

        Returns:
            int: self < valueで負の値，self == valueで0，self > valueで正の値
        """
        if not isinstance(value, _Range):
            raise TypeError()
        result_start: int
        if self.start is None:
            result_start = 0 if value.start is None else -1
        else:
            result_start = 1 if value.start is None else self.start - value.start
        if result_start != 0:
            return result_start
        result_end: int
        if self.end is None:
            result_end = 0 if value.end is None else 1
        else:
            result_end = -1 if value.end is None else self.end - value.end
        return result_end

    def __contains__(self, item: "int | _Point") -> bool:
        in_under: bool = self.start is None or self.start <= item
        in_top: bool = self.end is None or item <= self.end
        return in_under and in_top

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, _Range):
            return self.__start == __value.__start and self.__end == __value.__end
        if isinstance(__value, _Point | int):
            if self.start is None or self.end is None:
                return False
            return self.start == __value and self.start == self.end
        return False

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __lt__(self, __value: "_Range") -> bool:
        return self.__compare_to(__value) < 0

    def __le__(self, __value: "_Range") -> bool:
        return self.__compare_to(__value) <= 0

    def __gt__(self, __value: "_Range") -> bool:
        return self.__compare_to(__value) > 0

    def __ge__(self, __value: "_Range") -> bool:
        return self.__compare_to(__value) >= 0

    def __str__(self) -> str:
        result: str = "-"
        if self.start is not None:
            result = str(self.start) + result
        if self.end is not None:
            result += str(self.end)
        return result


class ValueRange:
    """値の範囲を表します。
    """

    @classmethod
    def create_as_all(cls) -> "ValueRange":
        result = cls()
        result.__is_all = True
        return result

    @property
    def is_all(self) -> bool:
        """全ての数を表すかどうかを取得します。
        """
        return self.__is_all

    def __init__(self, source: list[_Point | _Range] | None = None) -> None:
        """ValueRangeの新しいインスタンスを初期化します。

        Args:
            source (list[_Point | _Range]): 設定する範囲
        """
        self.__list: list[_Point | _Range] = source or []
        self.__is_all: bool = False

    @classmethod
    def parse(cls, value: str) -> "ValueRange":
        """文字列からValueRangeの新しいインスタンスを生成します。

        Args:
            value (str): 文字列

        Returns:
            ValueRange: valueから生成された新しいインスタンス
        """
        result = ValueRange()

        elements: list[str] = value.split(',')
        if any([i == "ALL" for i in elements]):
            result.__is_all = True
            return result
        for current in elements:
            if '-' in current:
                result.__add_range(_Range.parse(current))
            else:
                result.__add_point(_Point.parse(current))

        return result

    def iterate_values(self) -> Generator[_Point | _Range, None, None]:
        """インスタンスの持つ値と範囲を列挙します。

        Yields:
            Generator[_Point | _Range, None, None]: 値と範囲を列挙するジェネレータのインスタンス
        """
        yield from self.__list

    def __add_point(self, value: "_Point") -> None:
        """値を追加します。

        Args:
            value (_Point): 追加する値
        """
        if not value.value in self:
            self.__list.append(value)

    def __add_range(self, value: "_Range") -> None:
        """範囲を追加します。

        Args:
            value (_Range): 追加する範囲
        """
        self.__list.append(value)

    def __contains__(self, value: int):
        if self.is_all:
            return True
        for current in self.__list:
            if isinstance(current, _Point):
                if value == current:
                    return True
                continue
            if value in current:
                return True

    def __str__(self) -> str:
        if self.is_all:
            return "ALL"
        return str.join(',', [str(c) for c in self.__list])
