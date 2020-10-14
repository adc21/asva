import warnings
from typing import TypedDict
import numpy as np
from asva.dampers.Damper import Damper

class VDBType(TypedDict):
    c1: float
    c2: float
    vr: float
    vel_max: float

class VDB(Damper):
    def __init__(self, dt: float, Nd: float, c1: float, c2: float, vr: float, vel_max=1.5):
        super().__init__(dt, Nd)
        self.c1 = c1
        self.c2 = c2
        self.vr = vr
        self.vel_max = vel_max
        self.force: float = 0

    def step(self, dis: float):
        # init
        self.init_step(dis)

        sign = self.vel / abs(self.vel) if not self.vel == 0 else 1

        if abs(self.vel) < self.vr:
            self.force = sign*self.c1*abs(self.vel)*self.Nd
        else:
            self.force = sign*(self.c2*(abs(self.vel)-self.vr)+self.c1*self.vr)*self.Nd

        if abs(self.vel) > self.vel_max:
            warnings.warn("速度がダンパー許容最大速度%sを超えています。" % self.vel_max)

        # end
        self.end_step()
        return self.force

def VDB_MATRIX(n_dof: int, size: int, C: np.ndarray) -> np.ndarray:
    """応答倍率計算時のダンパーマトリクス"""
    MATRIX = np.zeros((size, size))

    if n_dof == 1:
        MATRIX[0, 0] = C[0]
    else:
        for n in range(n_dof):
            if n == 0:
                MATRIX[n, n] = C[n]+C[n+1]
                MATRIX[n, n+1] = -C[n+1]
            elif n == n_dof-1:
                MATRIX[n, n-1] = -C[n]
                MATRIX[n, n] = C[n]
            else:
                MATRIX[n, n-1] = -C[n]
                MATRIX[n, n] = C[n]+C[n+1]
                MATRIX[n, n+1] = -C[n+1]

    return MATRIX
