from subprocess import CompletedProcess
import subprocess

from .configuration import Configuration


class IqtreeManager:
    """IQ-TREEの実行を行います。
    """

    def __init__(self, config: Configuration) -> None:
        """IqtreeManagerの新しいインスタンスを初期化します。

        Args:
            config (Configuration): コンフィグ情報
        """
        self.__iqtree_command: str = config.iqtree_command
        self.__other_params: str = ""

    @property
    def other_params(self) -> str:
        """その他引数を取得または設定します。
        """
        return self.__other_params

    @other_params.setter
    def other_params(self, value: str) -> None:
        self.__other_params = value

    def load_other_params(self, path: str) -> None:
        """その他引数をファイルから読み取ります。

        Args:
            path (str): 読み取るファイル
        """
        with open(path, "rt") as io:
            text: str = io.read()
        self.__other_params = text.replace("\n", " ")

    def calc_sitelh(self,
                    sequence_path: str,
                    model: str,
                    input_tree_path: str,
                    target_trees_path: str,
                    verbose: bool = False,
                    redo: bool = False,
                    prefix: str | None = None,
                    threads: int | None = None,
                    cwd: str | None = None) -> CompletedProcess[bytes]:
        """尤度を計算してSITELHファイルを出力します。

        Args:
            sequence_path (str): 配列ファイルのパス
            model (str): 進化モデル
            input_tree_path (str): モデルフィッティングに用いるツリーのパス
            target_trees_path (str): 尤度計算を行うツリー一覧のパス
            verbose (bool, optional): ログを出力にリダイレクトするかどうか. Defaults to False.
            redo (bool, optional): --redo. Defaults to False.
            prefix (str | None, optional): --prefix. Defaults to None.
            threads (int | None, optional): -T. Defaults to None.
            cwd (str | None, optional): 実行ディレクトリ. Defaults to None.
        """
        command = f"-s {sequence_path} -m {model} -te {input_tree_path} -z {target_trees_path} -wsl"
        return self.__invoke_iqtree(command, verbose, redo, prefix, threads, cwd)

    def exec_autest(self,
                    sequence_path: str,
                    model: str,
                    input_tree_path: str,
                    treeset_path: str,
                    rellboot_count: int,
                    verbose: bool = False,
                    redo: bool = False,
                    prefix: str | None = None,
                    threads: int | None = None,
                    cwd: str | None = None) -> CompletedProcess[bytes]:
        """AU検定を実行します。

        Args:
            sequence_path (str): 配列ファイルのパス
            model (str): 進化モデル
            input_tree_path (str): ツリーファイルのパス
            treeset_path (str): 検証するツリー一覧のパス
            rellboot_count (int): RELL Bootstrapの試行回数（下限1000，10000以上推奨）
            verbose (bool, optional): ログを出力にリダイレクトするかどうか. Defaults to False.
            redo (bool, optional): --redo. Defaults to False.
            prefix (str | None, optional): --prefix. Defaults to None.
            threads (int | None, optional): -T. Defaults to None.
            cwd (str | None, optional): 実行ディレクトリ. Defaults to None.
        """
        command = f"-s {sequence_path} -m {model} -te {input_tree_path} -z {treeset_path} -zb {rellboot_count} -au"
        return self.__invoke_iqtree(command, verbose, redo, prefix, threads, cwd)

    def __invoke_iqtree(self, command: str, verbose: bool, redo: bool, prefix: str | None, threads: int | None, cwd: str | None) -> CompletedProcess[bytes]:
        """IQ-TREEを実行します。

        Args:
            command (str): コマンド
            verbose (bool): ログを出力にリダイレクトするかどうか
            redo (bool): --redoオプション
            prefix (str | None): --prefixオプション
            threads (int | None): -T オプション
            cwd (str | None): 実行ディレクトリ

        Returns:
            CompletedProcess[bytes]: subprocess.run()実行結果
        """
        command = f"{self.__iqtree_command} {command}"
        if threads is not None:
            command += f" -T {threads}"
        if not verbose:
            command += " --quiet"
        if redo:
            command += " --redo"
        if prefix is not None:
            command += f" --prefix {prefix}"
        if len(self.other_params) > 0:
            command += f" {self.other_params}"
        return subprocess.run(command, shell=True, cwd=cwd, check=True)
