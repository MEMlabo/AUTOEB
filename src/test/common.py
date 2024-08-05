import os


def get_test_data_dir() -> str:
    """テスト用データの配置されているディレクトリのパスを取得します。

    Returns:
        str: ディレクトリのパス（末尾にスラッシュ付き）
    """
    return os.path.dirname(__file__) + "/../TestData/"


def get_output_dir() -> str:
    """出力データの配置されているディレクトリのパスを取得します。

    Returns:
        str: ディレクトリのパス（末尾にスラッシュ付き）
    """
    result: str = os.path.dirname(__file__) + "/out/"
    if not os.path.isdir(result):
        os.mkdir(result)
    return result
