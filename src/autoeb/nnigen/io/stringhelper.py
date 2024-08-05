class _StringHelper:
    @classmethod
    def last_index(cls, value: str, substring: str, start: int | None = None, end: int | None = None) -> int:
        """指定した部分文字列のうち最後のもののインデックスを取得します。

        Args:
            value (str): 検索対象
            substring (str): 検索する部分文字列
            start (int | None, optional): 開始インデックス. Defaults to None.
            end (int | None, optional): 終了インデックス. Defaults to None.

        Returns:
            int: インデックス

        Raise:
            ValueError: 指定した部分文字列が見つからない
        """
        length: int = len(substring)
        if length == 0:
            return 0

        _start: int = len(value) - 1 if start is None else start
        _end: int = 0 if end is None else end + 1
        if len(substring) > 1:
            substring = substring[::-1]

        index: int
        short: str = value[_end:_start + 1][::-1]
        try:
            index = short.index(substring)
        except ValueError as e:
            raise e
        return len(short) - len(substring) - index + _end
