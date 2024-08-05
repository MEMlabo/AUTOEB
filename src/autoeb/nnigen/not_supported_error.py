class NotSupportedError(Exception):
    """サポートされていない機能に対するエラーのクラスです。
    """

    def __init__(self, *args: object) -> None:
        if len(args) == 0:
            args = ("This function is not supported",)
        super().__init__(*args)
