import regex

from .consts import RESULT_NG, RESULT_OK
from .catpv_result import CatpvResult


class OutputFormatter:
    __compatible_keys: set[str] = {
        'src',
        'bin',
        'p',
        'au-bin',
        'au-p',
        'sh-bin',
        'sh-p',
        'kh-bin',
        'kh-p',
        'wsh-bin',
        'wsh-p',
        'wkh-bin',
        'wkh-p',
        'dlnL',
        'pp',
        'bp',
        'mbp',
    }

    def __init__(self, format: str) -> None:
        """OutputFormatterの新しインスタンスを初期化します。

        Args:
            format (str): サポート値のフォーマット
        """
        self.__format: str = format

    @classmethod
    def check_format(cls, format: str) -> bool:
        """フォーマット文字列が正常かどうかを検証します。

        Args:
            format (str): 検証するフォーマット文字列

        Returns:
            bool: formatが有効の場合はTrue，それ以外でFalse
        """
        matches: list[str] = regex.findall(r"{(.*?)}", format)
        for current_key in matches:
            if not current_key in cls.__compatible_keys:
                return False
        return True

    def format(self, src: str, catpv: CatpvResult, sig_level: float) -> str:
        """出力ツリーの枝名を取得します。

        Args:
            src (str): 元の枝名
            catpv (CatpvResult): CATPVファイルの情報
            sig_level (float): 有意水準

        Returns:フォーマットされた枝名
        """

        # Formats of "fmt"
        #
        # {src}: Support values in given tree
        # {bin}, {au-bin}: 0/1 value by AU test
        # {p}, {au-p}: p-value of the alternative topology greater than the other by AU test
        # {sh-bin}: 0/1 value by SH test
        # {sh-p}: p-value of the alternative topology greater than the other by SH test
        # {kh-bin}: 0/1 value by KH test
        # {kh-p}: p-value of the alternative topology greater than the other by KH test
        # {wsh-bin}: 0/1 value by weighted SH test
        # {wsh-p}: p-value of the alternative topology greater than the other by weighted SH test
        # {wkh-bin}: 0/1 value by weighted KH test
        # {wkh-p}: p-value of the alternative topology greater than the other by weighted KH test
        # {dlnL}: Observed log-likelihood difference of the alternative topology less than the other
        # {pp}: Bayesian posterior probability of the ML tree
        # {bp}: Bootstrap probability of the ML tree
        # {mbp}: Bootstrap probability of the ML tree calculated from the multiscale bootstrap

        max_au_p: float = max(catpv.stat_nni1.au, catpv.stat_nni2.au)
        au_bin: str = RESULT_OK if sig_level > max_au_p else RESULT_NG
        max_sh_p: float = max(catpv.stat_nni1.sh, catpv.stat_nni2.sh)
        sh_bin: str = RESULT_OK if sig_level > max_sh_p else RESULT_NG
        max_kh_p: float = max(catpv.stat_nni1.kh, catpv.stat_nni2.kh)
        kh_bin: str = RESULT_OK if sig_level > max_kh_p else RESULT_NG
        max_wsh_p: float = max(catpv.stat_nni1.wsh, catpv.stat_nni2.wsh)
        wsh_bin: str = RESULT_OK if sig_level > max_wsh_p else RESULT_NG
        max_wkh_p: float = max(catpv.stat_nni1.wkh, catpv.stat_nni2.wkh)
        wkh_bin: str = RESULT_OK if sig_level > max_wkh_p else RESULT_NG
        min_obs: float = max(catpv.stat_nni1.obs, catpv.stat_nni2.obs)

        replace_dict: dict[str, object] = {
            'src': src,
            'bin': au_bin,
            'p': max_au_p,
            'au-bin': au_bin,
            'au-p': max_au_p,
            'sh-bin': sh_bin,
            'sh-p': max_sh_p,
            'kh-bin': kh_bin,
            'kh-p': max_kh_p,
            'wsh-bin': wsh_bin,
            'wsh-p': max_wsh_p,
            'wkh-bin': wkh_bin,
            'wkh-p': max_wkh_p,
            'dlnL': min_obs,
            'pp': catpv.stat_ml.pp,
            'bp': '{:.01f}'.format(catpv.stat_ml.brell * 100),
            'mbp': '{:.01f}'.format(catpv.stat_ml.np * 100),
        }

        return self.__format.format(**replace_dict)
