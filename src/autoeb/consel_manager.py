from io import TextIOWrapper
import os
import subprocess
from subprocess import CompletedProcess

from .configuration import Configuration


class ConselManager:
    DIR_FROM_PATH: str = "$PATH"

    def __init__(self, config: Configuration) -> None:
        self.__consel_dir: str = config.consel_dir

    def makermt(self, sitelh_path: str, seed: int, rellboot: int, cwd: str | None = None, stdout: TextIOWrapper | None = None) -> CompletedProcess[bytes]:
        """makermtを実行します。

        Args:
            sitelh_path (str): SITELHファイルのパス
            seed (int): 乱数のシード値
            rellboot (int): RELL bootstrap複製数
            cwd (str | None, optional): 実行ディレクトリ. Defaults to None.
            stdout (TextIOWrapper | None, optional): 出力先. Defaults to None.
        """
        opt_b: float = rellboot / 10000
        command = f"--puzzle {sitelh_path} -b {opt_b} -s {seed}"
        return self.__invoke_app("makermt", command, cwd, stdout)

    def consel(self, rmt_path: str, cwd: str | None = None, stdout: TextIOWrapper | None = None) -> CompletedProcess[bytes]:
        """conselを実行します。

        Args:
            rmt_path (str): RMTファイルのパス
            cwd (str | None, optional): 実行ディレクトリ. Defaults to None.
            stdout (TextIOWrapper | None, optional): 出力先. Defaults to None.
        """
        command = f"{rmt_path}"
        return self.__invoke_app("consel", command, cwd, stdout)

    def catpv(self, pv_path: str, cwd: str | None = None, stdout: TextIOWrapper | None = None) -> CompletedProcess[bytes]:
        """catpvを実行します。

        Args:
            pv_path (str): PVファイルのパス
            cwd (str | None, optional): 実行ディレクトリ. Defaults to None.
            stdout (TextIOWrapper | None, optional): 出力先. Defaults to None.
        """
        command = f"{pv_path}"
        return self.__invoke_app("catpv", command, cwd, stdout)

    def __get_app_path(self, appname: str) -> str:
        """アプリケーションのパスを取得します。

        Args:
            appname (str): アプリケーション名

        Returns:
            str: アプリケーションのパス
        """
        if self.__consel_dir == self.DIR_FROM_PATH:
            return appname
        return os.path.join(self.__consel_dir, appname)

    def __invoke_app(self, appname: str, command: str, cwd: str | None, stdout: TextIOWrapper | None) -> CompletedProcess[bytes]:
        """アプリを実行します。

        Args:
            appname (str): アプリ名
            command (str): コマンド
            cwd (str | None): 実行ディレクトリ
            stdout (TextIOWrapper | None, optional): 出力先

        Returns:
            CompletedProcess[bytes]: subprocess.run()の実行結果
        """
        command = f"{self.__get_app_path(appname)} {command}"
        return subprocess.run(command, shell=True, cwd=cwd, check=True, stdout=stdout)
