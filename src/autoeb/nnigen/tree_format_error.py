class TreeFormatError(Exception):
    """系統樹のフォーマットが無効な場合を表すエラーのクラスです。
    """

    def __init__(self, *args: object) -> None:
        if len(args) == 0:
            args = ("Invalid tree format is detected",)
        super().__init__(*args)
