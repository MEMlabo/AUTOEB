from io import TextIOWrapper
import regex
from regex import Pattern
from typing import overload

from .statistics_entry import StatisticsEntry


class CatpvResult:
    __split_regex: Pattern = regex.compile(r"\s+")

    """catpvの結果を表します。
    """
    @property
    def stat_ml(self) -> StatisticsEntry:
        """最尤系統樹の系統情報を取得します。
        """
        return self.__stat[0]

    @property
    def stat_nni1(self) -> StatisticsEntry:
        """NNIによる系統樹の系統情報を取得します。
        """
        return self.__stat[1]

    @property
    def stat_nni2(self) -> StatisticsEntry:
        """NNIによる系統樹の系統情報を取得します。
        """
        return self.__stat[2]

    def __init__(self) -> None:
        """CatpvResultの新しいインスタンスを初期化します。
        """
        self.__stat: list[StatisticsEntry] = list[StatisticsEntry]()

    @classmethod
    @overload
    def load(cls, source: str) -> "list[CatpvResult]":
        ...

    @classmethod
    @overload
    def load(cls, source: TextIOWrapper) -> "list[CatpvResult]":
        ...

    @classmethod
    def load(cls, source: str | TextIOWrapper) -> "list[CatpvResult]":
        """catpvの出力からインスタンスを生成します。

        Args:
            source (str | TextIOWrapper): 読み込む出力のファイルパスまたはストリームオブジェクト

        Returns:
            list[CatpvResult]: 生成されたCatpvResultのインスタンス一覧
        """
        if isinstance(source, str):
            with open(source, "rt") as io:
                return cls.load(io)

        result = list[CatpvResult]()
        current: CatpvResult | None = None
        labels = list[str]()
        while True:
            line: str = source.readline()
            if line == "":
                break
            line = line.strip()
            if not line.startswith("# "):
                if current is not None:
                    current = None
                    labels.clear()
                continue
            line = line[2:].strip()
            if line.startswith("reading "):
                current = cls()
                result.append(current)
                continue
            if current is not None:
                if len(current.__stat) == 0 and len(labels) == 0:
                    labels = cls.__split_regex.split(line)
                else:
                    elements: list[str] = cls.__split_regex.split(line)
                    stat_values = dict[str, str]()
                    for index in range(len(labels)):
                        if labels[index] == '|':
                            continue
                        stat_values[labels[index]] = elements[index]
                    current.__stat.append(StatisticsEntry.from_table_dict(stat_values))
                    current.__stat.sort(key=lambda x: x.index)

        return result
