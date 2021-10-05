# asva
[![Python Versions](https://img.shields.io/pypi/pyversions/asva.svg)](https://pypi.org/project/asva/)
[![PyPI version](https://img.shields.io/pypi/v/asva)](https://pypi.org/pypi/asva/)
[![Downloads](https://pepy.tech/badge/asva)](https://pepy.tech/project/asva)
[![Documentation Status](https://readthedocs.org/projects/asva/badge/?version=latest)](https://asva.readthedocs.io/en/latest/?badge=latest)

質点系による振動解析プログラム

## 概要

asva は Python による質点系の振動解析プログラムです。現在、次のような機能が実装されています。

- 固有値解析
- 地震応答解析
- 応答倍率計算
  etc.

## ドキュメント

詳しくは[ドキュメント](https://asva.readthedocs.io/en/latest/)を確認してください。

## 必要なもの

- Python3.8+

## 使い方

### インストールとインポート

#### ・pypiからインストールして使う場合
```
pip install asva
```
```python
import asva as ap
```

#### ・asvaのコードを直接修正しながら使う場合
以下のようにrequirements.txtをインストールした上で、asvaをフォルダを任意の場所に配置
```
pip install -r path/to/asva/requirements.txt
```
```python
import path.to.asva as ap
```

### コード例

```python
import asva as ap

config: ap.AnalysisConfigType = {
    # analysis
    'BETA': 1 / 4,

    # case
    'CASES': [
        {
            'NAME': 'Example',
            'WAVE': 'Sample',
            'AMP': 1,
            'DAMPER': 'None',
            'NDIV': 2,
            'START_TIME': 0,
            'END_TIME': None,
        },
    ],

    # damper
    'DAMPERS': {
        'None': [
            [],
        ],
    },

    # model
    'BASE_ISOLATION': False,
    'H': 0.02,
    'H_TYPE': 0,
    'I': [
        [1],
    ],
    'MI': [100],
    'KI': [
        [{
            'type': 'elastic',
            'k0': 4000,
        }, ],
    ],

    # wave
    'WAVES': {
        'Sample': {
            'NAME': 'Sample',
            'DT': 0.02,
            'NDATA': 2688,
            'TO_METER': 0.01,
            'INPUT_FILE': 'wave/Sample.csv',
            'DELIMITER': None,
            'SKIPROWS': 3,
            'COL': 0,
            'ENCORDING': 'utf',
        },
    },
}


def main():
    analysis = ap.Analysis(config, 0)   # ０は最初のケースを回す。
    analysis.analysis()
    print(analysis.resp.dis)

if __name__ == '__main__':
    main()


```

### Config の設定

Config では、解析モデルや解析方法、出力設定を Dict で指定します。
設定方法は以下の通りです。
詳細なタイプの確認は[Types](https://github.com/adc21/asva/blob/master/asva/Types.py)を確認してください。

```python
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
```

## 履歴則

現在以下の履歴則が組み込まれています。

| 名称       | タイプキー | 備考 |
| ---------- | ---------- | ---- |
| 弾性       | elastic    |      |
| バイリニア | bilinear   |      |
| トリリニア | trilinear  |      |
| 逆行型     | gyakko     |      |
| 武田モデル | takeda     |      |

## ダンパー

現在以下のダンパーが組み込まれています。

| 名称                       | タイプキー | 時刻歴計算 | 応答倍率計算 | 備考                     |
| -------------------------- | ---------- | ---------- | ------------ | ------------------------ |
| 質量ダンパー               | MASS       | ○          | ○            | 層間加速度に比例する要素 |
| ストッパー                 | Stopper    | ○          | ×            |                          |
| 粘性ダンパー（CV^α）       | VDA        | ○          | ○            |                          |
| 粘性ダンパー（バイリニア） | VDB        | ○          | ○            |                          |
| TMD                        | TMD        | ○          | ○            |                          |
| iRDT                       | iRDT       | ○          | ○            |                          |

## ご使用にあたって

asva は開発中のため、間違っている場合や不正確な場合があります。何かありましたら[issues](https://github.com/adc21/asva/issues)にお知らせください。
