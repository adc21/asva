"""VDA の抵抗力
"""
from typing import TypedDict, Optional
import warnings
import numpy as np

from asva.dampers.Damper import Damper


class VDAType(TypedDict):
    cd: float
    alpha: float
    vy: Optional[float]
    vel_max: Optional[float]


class VDA(Damper):
    def __init__(self, dt: float, Nd: float, cd: float, alpha: float, vy=None, vel_max=None):
        super().__init__(dt, Nd)
        self.cd = cd
        self.alpha = alpha
        self.vy = vy if vy else 0.001
        self.vel_max = vel_max if vel_max else 1.5
        self.force: float = 0

    def step(self, dis: float):
        # init
        self.init_step(dis)

        sign = self.vel / abs(self.vel) if self.vel != 0 else 1

        if abs(self.vel) <= self.vy:
            ce = self.cd*self.vy**(self.alpha-1)
            self.force = ce * self.vel * self.Nd
        else:
            # ce = cd*self.alpha*abs(v)**(self.alpha-1)
            self.force = sign * self.cd * (abs(self.vel)**self.alpha) * self.Nd

        if abs(self.vel) > self.vel_max:
            warnings.warn("速度がダンパー許容最大速度%sm/sを超えています。" % self.vel_max)

        # end
        self.end_step()
        return self.force


def VDA_MATRIX(n_dof: int, size: int, C: np.ndarray) -> np.ndarray:
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
