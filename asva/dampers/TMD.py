"""TMD の抵抗力
"""
from typing import TypedDict, Tuple
import numpy as np
from asva.dampers.Damper import Damper

class TMDType(TypedDict):
    md: float
    cd: float
    kd: float

beta = 1/4

def nmb(m1: float, c1: float, k1: float, dt: float, ff: float, acc1: float, vel1: float, dis1: float) -> Tuple[float, float, float]:
    acc2: float = (ff-c1*(vel1+0.5*dt*acc1)-k1*(dis1+dt*vel1+(0.5-beta)*dt*dt*acc1))/(m1+c1*0.5*dt+k1*beta*dt*dt)
    vel2: float = vel1+0.5*dt*(acc1+acc2)
    dis2: float = dis1+dt*vel1+(0.5-beta)*dt*dt*acc1+beta*dt*dt*acc2
    return acc2, vel2, dis2

class TMD(Damper):
    def __init__(self, dt: float, Nd: float, md: float, cd: float, kd: float):
        super().__init__(dt, Nd)
        self.md = md
        self.cd = cd
        self.kd = kd
        self.acc2: float = 0
        self.vel2: float = 0
        self.dis2: float = 0
        self.force: float = 0

    def step(self, a_acc: float):
        ff = -self.md*self.Nd*a_acc
        self.acc2, self.vel2, self.dis2 = nmb(self.md*self.Nd, self.cd*self.Nd, self.kd*self.Nd, self.dt, ff, self.acc2, self.vel2, self.dis2)
        self.force = -self.md*(a_acc + self.acc2) * self.Nd # self.kd*self.Nd*self.dis2 + self.cd*self.Nd*self.vel2
        return self.force

def TMD_MATRIX(n_dof: int, M: np.ndarray, C: np.ndarray, K: np.ndarray, I: np.ndarray, MD: np.ndarray, CD: np.ndarray, KD: np.ndarray) -> np.ndarray:
    """応答倍率計算時のダンパーマトリクス（MD,CD,KDの値は１層あたり１種類のみとすること）"""
    assert MD.size == n_dof, f"MD size must be same as n_dof ${n_dof}"

    size = np.size(M,0)
    matrix_size = size + n_dof

    C_MATRIX = np.zeros((matrix_size, matrix_size))
    K_MATRIX = np.zeros((matrix_size, matrix_size))
    M2 = np.concatenate((np.concatenate((M, np.zeros((n_dof, size)))), np.concatenate((np.zeros((size, n_dof)), np.diag(MD)))), axis=1)
    C2 = np.concatenate((np.concatenate((C, np.zeros((n_dof, size)))), np.concatenate((np.zeros((size, n_dof)), np.zeros((n_dof, n_dof))))), axis=1)
    K2 = np.concatenate((np.concatenate((K, np.zeros((n_dof, size)))), np.concatenate((np.zeros((size, n_dof)), np.zeros((n_dof, n_dof))))), axis=1)
    I2 = np.concatenate((I, np.eye(n_dof, 1)))

    for n in range(n_dof):
        C_MATRIX[n, n] = CD[n]
        C_MATRIX[n, n+size] = -CD[n]
        C_MATRIX[n+size, n] = -CD[n]
        C_MATRIX[n+size, n+size] = CD[n]
        K_MATRIX[n, n] = KD[n]
        K_MATRIX[n, n+size] = -KD[n]
        K_MATRIX[n+size, n] = -KD[n]
        K_MATRIX[n+size, n+size] = KD[n]

    return M2, C2, K2, I2, C_MATRIX, K_MATRIX
