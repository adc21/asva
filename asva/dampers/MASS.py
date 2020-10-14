from typing import TypedDict
import numpy as np
from asva.dampers.Damper import Damper

class MASSType(TypedDict):
    m: float

class MASS(Damper):
    def __init__(self, dt: float, Nd: float, m: float):
        super().__init__(dt, Nd)
        self.m = m
        self.force: float = 0

    def step(self, dis: float):
        # init
        self.init_step(dis)

        self.force = self.m * self.acc * self.Nd

        # end
        self.end_step()
        return self.force

def MASS_MATRIX(n_dof: int, size: int, M: np.ndarray) -> np.ndarray:
    """応答倍率計算時のダンパーマトリクス"""
    MATRIX = np.zeros((size, size))

    if n_dof == 1:
        MATRIX[0, 0] = M[0]
    else:
        for n in range(n_dof):
            if n == 0:
                MATRIX[n, n] = M[n]+M[n+1]
                MATRIX[n, n+1] = -M[n+1]
            elif n == n_dof-1:
                MATRIX[n, n-1] = -M[n]
                MATRIX[n, n] = M[n]
            else:
                MATRIX[n, n-1] = -M[n]
                MATRIX[n, n] = M[n]+M[n+1]
                MATRIX[n, n+1] = -M[n+1]

    return MATRIX
