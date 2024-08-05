class StatisticsEntry:
    """catpvの樹形比較の結果を表します。
    """

    @property
    def rank(self) -> int:
        return self.__rank

    @property
    def index(self) -> int:
        return self.__index

    @property
    def obs(self) -> float:
        return self.__obs

    @property
    def au(self) -> float:
        return self.__au

    @property
    def np(self) -> float:
        return self.__np

    @property
    def brell(self) -> float:
        return self.__brell

    @property
    def pp(self) -> float:
        return self.__pp

    @property
    def kh(self) -> float:
        return self.__kh

    @property
    def sh(self) -> float:
        return self.__sh

    @property
    def wkh(self) -> float:
        return self.__wkh

    @property
    def wsh(self) -> float:
        return self.__wsh

    def __init__(self,
                 rank: int,
                 index: int,
                 obs: float,
                 au: float,
                 np: float,
                 brell: float,
                 pp: float,
                 kh: float,
                 sh: float,
                 wkh: float,
                 wsh: float
                 ) -> None:
        """StatisticsEntryの新しいインスタンスを初期化します。

        Args:
            rank (int): ranking
            index (int): Tree index
            obs (float): 
            au (float): AU-Test
            np (float): 
            brell (float): RELL boot
            pp (float): 
            kh (float): KH-Test
            sh (float): SH-Test
            wkh (float): 
            wsh (float): 
        """
        self.__index: int = index
        self.__rank: int = rank
        self.__obs: float = obs
        self.__au: float = au
        self.__np: float = np
        self.__brell: float = brell
        self.__pp: float = pp
        self.__kh: float = kh
        self.__sh: float = sh
        self.__wkh: float = wkh
        self.__wsh: float = wsh

    @classmethod
    def from_table_dict(cls, source: dict[str, str]) -> "StatisticsEntry":
        """IQTREEのテーブルのエントリを表す辞書からStatisticsEntryの新しいインスタンスを生成します。

        Args:
            source (dict[str, str]): 読み込む辞書

        Returns:
            StatisticsEntry: StatisticsEntryの新しいインスタンス
        """
        rank: int = int(source["rank"])
        index: int = int(source["item"])
        obs: float = float(source["obs"])
        au: float = float(source["au"])
        np: float = float(source["np"])
        brell: float = float(source["bp"])
        pp: float = float(source["pp"])
        kh: float = float(source["kh"])
        sh: float = float(source["sh"])
        wkh: float = float(source["wkh"])
        wsh: float = float(source["wsh"])
        return cls(rank, index, obs, au, np, brell, pp, kh, sh, wkh, wsh)
