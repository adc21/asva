===========================================================
Setup Config
===========================================================

Config dict must be provided to Analysis class in asva.
asva provides types to validate the dict. Types are defined in `Types <https://github.com/adc21/asva/blob/master/asva/Types.py>`_.
You can use them as shown below if needed.

.. code::

    import asva as ap

    analysis_config: ap.AnalysisConfigType = {
        <your config>
    }

    # optional
    amp_config: ap.AmplitudeConfigType = {
        <your config>
    }

    # optional
    export_config: ap.ExportConfigType = {
        <your config>
    }

    analysis = ap.Analysis(analysis_config, 0, amp_config, export_config)

Analysis Config
===============

.. code::

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
        KI: List[KIType]      # 主系の剛性[kN/m]

        # damper
        DAMPERS: Dict[str, List[List[DamperType]]]
                                    # ダンパーのリスト


Amplitude Config
================

.. code::

    class AmplitudeConfigType(TypedDict):
        N_W: int                    # 応答倍率曲線の出力データ数
        DF: float                   # 応答倍率曲線の出力周波数刻み[Hz]

Export Config
=============

.. code::

    class ExportConfigType(TypedDict):
        RESULT_DIR: str             # 解析結果のディレクトリ名
        RESULT_DATA_DIR_NAME: str   # 解析結果数値データのディレクトリ名
        RESULT_PLOT_DIR_NAME: str   # 解析結果プロットのディレクトリ名
        DATA_PLOT_STORIES: Optional[List[int]]  # 解析結果プロットで出力する層 (配列 or Noneで全指定)
