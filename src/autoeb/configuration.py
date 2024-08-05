import os
from typing import final

from .json_helper import deserialize, serialize


@final
class Configuration:
    """コンフィグを表します。
    """

    def __init__(self) -> None:
        self.__iqtree_command: str = "iqtree"
        self.__consel_dir: str = "$PATH"
        """CONSELのディレクトリ。$PATHで無指定
        """

    @property
    def iqtree_command(self) -> str:
        """IQ-TREEの起動コマンドを取得します。
        """
        return self.__iqtree_command

    @iqtree_command.setter
    def iqtree_command(self, value: str) -> None:
        """IQ-TREEの起動コマンドを設定します。
        """
        self.__iqtree_command = value

    @property
    def consel_dir(self) -> str:
        """CONSELのディレクトリを取得します。
        """
        return self.__consel_dir

    @consel_dir.setter
    def consel_dir(self, value: str) -> None:
        """CONSELのディレクトリを設定します。
        """
        self.__consel_dir = value

    @classmethod
    def get_config_path(cls) -> str:
        """コンフィグファイルのパスを取得します。

        Returns:
            str: コンフィグファイルのパス
        """
        return os.path.join(os.path.dirname(__file__), "config.json")

    @classmethod
    def load(cls) -> "Configuration":
        """設定を読み込みます。

        Returns:
            Configuration: 読み込んだ設定。ファイルが存在しない場合はデフォルトのインスタンス
        """
        path: str = cls.get_config_path()
        if os.path.isfile(path):
            with open(path, "r") as io:
                return deserialize(io.read(-1), Configuration)
        else:
            return cls()

    def save(self) -> None:
        """設定を保存します。
        """
        json: str = serialize(self)
        with open(self.get_config_path(), "wt") as io:
            io.write(json)

    def __str__(self) -> str:
        return serialize(self)
