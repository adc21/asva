from typing import Dict, Literal, Union, TypedDict, Optional, List
from asva.dampers import iRDTType, MASSType, VDAType, VDBType, TMDType, StopperType


class WaveType(TypedDict):
    NAME: str                   # 地震動名
    DT: float                   # 地震動のサンプリング時間刻み
    NDATA: int                  # 地震データ数
    TO_METER: float             # 地震データをm単位に変換する倍率
    INPUT_FILE: str             # 地震データファイル（拡張子含む）
    DELIMITER: Optional[str]    # 地震データの区切り文字 (スペース: None, カンマ:",")
    SKIPROWS: int               # 地震データの飛ばし行数
    COL: int                    # 地震データの読み込み列（１行目が0）
    ENCORDING: str              # 地震データのエンコード（デフォルトはshift-jis）


class CASESType(TypedDict):
    NAME: str
    WAVE: str                       # wave.py WAVESのキーを指定
    AMP: float                      # 地震波の入力倍率
    DAMPER: str                     # damper.py DAMPERSのキーを指定
    NDIV: int                       # 時間刻み
    START_TIME: Union[float, None]  # 地震波入力の開始時刻[s] Noneの場合は0
    END_TIME: Union[float, None]    # 地震波入力の終了時刻[s] Noneの場合は地震波の終了時刻

class BaseStiffStiffnessType(TypedDict):
    n1: int
    n2: int

class ElasticType(BaseStiffStiffnessType):
    type: Literal["elastic"]
    k0: float                       # 初期剛性[kN/m]


class BilinearType(BaseStiffStiffnessType):
    type: Literal["bilinear"]
    k0: float                       # 初期剛性[kN/m]
    a1: float                       # 降伏後剛性低下率[-]
    f1: float                       # 降伏荷重[kN]


class TrilinearType(BaseStiffStiffnessType):
    type: Literal["gyakko", "takeda", "trilinear"]
    k0: float                       # 初期剛性[kN/m]
    a1: float                       # 降伏後剛性低下率1[-]
    a2: float                       # 降伏後剛性低下率2[-]
    f1: float                       # 降伏荷重1[kN]
    f2: float                       # 降伏荷重2[kN]


KIType = Union[ElasticType, BilinearType, TrilinearType]

DamperTypes = Literal["VDA", "iRDT", "VDB", "MASS", "TMD", "Stopper"]
DamperProperties = Union[VDAType, iRDTType, MASSType, VDBType, TMDType, StopperType, None]


class DamperType(TypedDict):
    type: DamperTypes
    Nd: float
    d: DamperProperties


class AnalysisConfigType(TypedDict):
    # analysis
    BETA: float                 # Newmarkβ法のβ
    BASE_ISOLATION: bool        # 剛性比例型の減衰計算で1層目を無視(C1を0)

    # wave
    WAVES: Dict[str, WaveType]   # 地震波の設定

    # case
    CASES: List[CASESType]        # 解析ケースのリスト

    # model
    H: float                    # 主系粘性減衰定数
    H_TYPE: Literal[0, 1]       # 0: 初期剛性比例型　1: 瞬間合成比例型
    I: List[List[float]]        # インプットする外力（NDOF×1）の行列で指定。地震波入力の場合、通常全て1。
    MI: List[float]             # 主系の質量[ton]
    KI: List[KIType]            # 主系の剛性[kN/m]

    # damper
    DAMPERS: Dict[str, List[List[DamperType]]]
                                # ダンパーのリスト


class AmplitudeConfigType(TypedDict):
    N_W: int                    # 応答倍率曲線の出力データ数
    DF: float                   # 応答倍率曲線の出力周波数刻み[Hz]


class ExportConfigType(TypedDict):
    RESULT_DIR: str             # 解析結果のディレクトリ名
    RESULT_DATA_DIR_NAME: str   # 解析結果数値データのディレクトリ名
    RESULT_PLOT_DIR_NAME: str   # 解析結果プロットのディレクトリ名
    DATA_PLOT_STORIES: Optional[List[int]]  # 解析結果プロットで出力する層 (配列 or Noneで全指定)


class AsvaAnalysisConfigType(AnalysisConfigType):
    G: float                    # 重力加速度
    TEST: bool

class AsvaAmplitudeConfigType(AmplitudeConfigType):
    MAX_NK: int
    MAX_ND: List[int]

class AsvaExportConfigType(ExportConfigType):
    RESULT_DATA_CASES_DIR: List[str]
    RESULT_DATA_DIR: List[str]
    RESULT_PLOT_DIR: List[str]
