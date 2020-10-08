from typing import List, TypedDict, Union, Literal

from asva.src.Types import KIType
from asva.src.restoring_force.Elastic import Elastic
from asva.src.restoring_force.Bilinear import Bilinear
from asva.src.restoring_force.Trilinear import Trilinear
from asva.src.restoring_force.Gyakko import Gyakko
from asva.src.restoring_force.Takeda import Takeda

class ElasticType(TypedDict):
    type: Literal["elastic"]
    k0: float

class BilinearType(TypedDict):
    type: Literal["bilinear"]
    k0: float
    a1: float
    f1: float

class TrilinearType(TypedDict):
    type: Literal["gyakko", "takeda", "trilinear"]
    k0: float
    a1: float
    a2: float
    f1: float
    f2: float

KFType = Union[Elastic, Bilinear, Trilinear, Gyakko, Takeda]

def create_restoring_instances(n_dof: int, max_nk: int, KF):
    k: List[List[KFType]] = []
    for i in range(n_dof):
        row: List[KFType] = []
        for ii in range(max_nk):
            try:
                kf = KF[i][ii]
            except IndexError:
                continue

            # 弾性
            if kf["type"] == "elastic":
                row.append(Elastic(kf["k0"]))
            elif kf["type"] == "bilinear":
                row.append(Bilinear(kf["k0"], kf["a1"], kf["f1"]))
            elif kf["type"] == "trilinear":
                row.append(Trilinear(kf["k0"], kf["a1"], kf["a2"], kf["f1"], kf["f2"]))
            elif kf["type"] == "gyakko":
                row.append(Gyakko(kf["k0"], kf["a1"], kf["a2"], kf["f1"], kf["f2"]))
            elif kf["type"] == "takeda":
                row.append(Takeda(kf["k0"], kf["a1"], kf["a2"], kf["f1"], kf["f2"]))
            else:
                raise ValueError("No match type specified for KF")

        k.append(row)

    return k

def check_elastic(n_dof: int, max_nk: int, KF) -> bool:
    elastic = True
    for i in range(n_dof):
        for ii in range(max_nk):
            try:
                kf = KF[i][ii]
            except IndexError:
                continue

            if kf["type"] != "elastic":
                elastic = False

    return elastic

def calc_max_nk(KF: List[List[KIType]]) -> int:
    MAX_NK = 0
    for _, KF_I in enumerate(KF):
        MAX_NK = len(KF_I) if len(KF_I) > MAX_NK else MAX_NK

    return MAX_NK