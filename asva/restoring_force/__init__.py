from typing import List, TypedDict, Union, Literal

from asva.Types import KIType
from asva.restoring_force.Elastic import Elastic
from asva.restoring_force.Bilinear import Bilinear
from asva.restoring_force.Trilinear import Trilinear
from asva.restoring_force.Gyakko import Gyakko
from asva.restoring_force.Takeda import Takeda

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

def create_restoring_instances(KF: List[KFType]) -> List[KFType]:
    k: List[KFType] = []
    for _, kf in enumerate(KF):
        if kf["type"] == "elastic":
            k.append(Elastic(kf["n1"], kf["n2"], kf["k0"]))
        elif kf["type"] == "bilinear":
            k.append(Bilinear(kf["n1"], kf["n2"], kf["k0"], kf["a1"], kf["f1"]))
        elif kf["type"] == "trilinear":
            k.append(Trilinear(kf["n1"], kf["n2"], kf["k0"], kf["a1"], kf["a2"], kf["f1"], kf["f2"]))
        elif kf["type"] == "gyakko":
            k.append(Gyakko(kf["n1"], kf["n2"], kf["k0"], kf["a1"], kf["a2"], kf["f1"], kf["f2"]))
        elif kf["type"] == "takeda":
            k.append(Takeda(kf["n1"], kf["n2"], kf["k0"], kf["a1"], kf["a2"], kf["f1"], kf["f2"]))
        else:
            raise ValueError("Invalid type specified for KF")

    return k
