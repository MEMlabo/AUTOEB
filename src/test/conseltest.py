import unittest
from autoeb import CatpvResult, StatisticsEntry

from test.common import get_test_data_dir


class ConselTest(unittest.TestCase):
    """CONSEL関連のユニットテストを行うクラスです。
    """

    @classmethod
    def __compare_statistical_entry(cls,
                                    stat: StatisticsEntry,
                                    rank: int,
                                    item: int,
                                    obs: float,
                                    au: float,
                                    np: float,
                                    bp: float,
                                    pp: float,
                                    kh: float,
                                    sh: float,
                                    wkh: float,
                                    wsh: float) -> None:
        """StatisticsEntryの値を検証します。

        Args:
            stat (StatisticsEntry): 検証するインスタンス
            rank (int): 
            item (int): 
            obs (float): 
            au (float): 
            np (float): 
            bp (float): 
            pp (float): 
            kh (float): 
            sh (float): 
            wkh (float): 
            wsh (float): 
        """
        assert stat.rank == rank
        assert stat.index == item
        assert stat.obs == obs
        assert stat.au == au
        assert stat.np == np
        assert stat.brell == bp
        assert stat.pp == pp
        assert stat.kh == kh
        assert stat.sh == sh
        assert stat.wkh == wkh
        assert stat.wsh == wsh

    def test_read_catpv(self) -> None:
        """catpvの出力の読み込みをテストします。
        """
        catpv: CatpvResult = CatpvResult.load(get_test_data_dir() + "catpv.txt")[0]
        self.__compare_statistical_entry(catpv.stat_ml, 3, 1, 0.1, 0.320, 0.307, 0.307, 0.314, 0.318, 0.318, 0.318, 0.318)
        self.__compare_statistical_entry(catpv.stat_nni1, 1, 2, -0.0, 0.596, 0.446, 0.441, 0.343, 0.563, 0.731, 0.563, 0.733)
        self.__compare_statistical_entry(catpv.stat_nni2, 2, 3, 0.0, 0.503, 0.263, 0.259, 0.343, 0.437, 0.760, 0.437, 0.759)
