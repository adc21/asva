from typing import Tuple, List

import numpy as np
import numpy.linalg as LA

from asva.Types import KIType
from asva.utils.normalize import normalize_eig
from asva.restoring_force import create_restoring_instances

class Model:
    def __init__(self, h: float, h_type: int, MI: List[float], KI: List[KIType], I: List[List[float]], base_isolation: bool = False):
        self.n_dof = len(MI)
        self.amp_size = self.n_dof
        self.h = h
        self.h_type = h_type
        assert(self.h_type == 0 or self.h_type == 1)

        self.base_isolation = base_isolation
        self.KI = KI

        self.ki = create_restoring_instances(self.KI)
        self.fk = np.zeros(len(self.KI))  # 各層各要素現ステップの復原力

        self.MF = np.array(MI)
        self.Mt = np.sum(self.MF)
        self.M = np.diag(self.MF)
        self.K = self.KMatrix()
        self.K0 = self.K
        self.C = self.calc_C(self.K)
        self.C0 = self.C
        self.I = np.array(I)
        self.w0, self.v0 = self.eig(self.M, self.K0)    # 固有角振動数, 固有ベクトル
        length = len(self.w0)
        self.m0 = np.zeros((length))            # 広義質量
        self.me = np.zeros((length))            # 有効質量
        self.r_me = np.zeros((length))          # 有効質量比
        self.k0 = np.zeros((length))            # 広義剛性
        self.b = np.zeros((length))             # 刺激係数
        self.vb = np.zeros((length, length))    # 刺激関数

        for i, v in enumerate(self.v0):
            self.m0[i] = np.dot(np.dot(v.T, self.M), v)
            self.k0[i] = np.dot(np.dot(v.T, self.K0), v)
            self.b[i] = np.dot(np.dot(v.T, self.M), self.I) / self.m0[i]
            self.me[i] = self.b[i]**2 * self.m0[i]
            self.r_me[i] = self.me[i] / self.Mt
            self.vb[i] = np.dot(v, self.b[i])

        for i in range(len(self.v0)):
            if abs(np.sum(self.vb[:, i]) - 1) > 1e-4:   # 各次数の刺激関数の和が１
                raise ValueError('固有値解析が正しくない可能性があります。')

    def KMatrix(self) -> np.ndarray:
        K = np.zeros((self.n_dof, self.n_dof))

        for _, ki in enumerate(self.ki):
            if ki.n1 == 0:
                K[ki.n2-1, ki.n2-1] += ki.k
            else:
                K[ki.n1-1, ki.n1-1] += ki.k
                K[ki.n1-1, ki.n2-1] += -ki.k
                K[ki.n2-1, ki.n1-1] += -ki.k
                K[ki.n2-1, ki.n2-1] += ki.k

        return K

    def upper_K(self):
        """最下層を節点に持つ剛性を除いた剛性マトリクス"""
        K = np.zeros((self.n_dof-1, self.n_dof-1))

        for _, ki in enumerate(self.ki):
            if ki.n1 == 0:
                pass
            elif ki.n1 == 1:
                K[ki.n2-2, ki.n2-2] += ki.k0
            else:
                K[ki.n1-2, ki.n1-2] += ki.k0
                K[ki.n1-2, ki.n2-2] += -ki.k0
                K[ki.n2-2, ki.n1-2] += -ki.k0
                K[ki.n2-2, ki.n2-2] += ki.k0

        return K

    @property
    def Fk(self):
        Fk = np.zeros((self.n_dof, 1))  # 各層現ステップのダンパー力

        for _, ki in enumerate(self.ki):
            if ki.n1 == 0:
                Fk[ki.n2-1] += ki.force
            else:
                Fk[ki.n1-1] += -ki.force
                Fk[ki.n2-1] += ki.force

        return Fk

    def calc_C(self, K):
        if self.base_isolation:
            if self.n_dof == 1:
                C = np.zeros((self.n_dof))
                return C
            else:
                K[0, 0] = self.ki[1].k0

            # 基礎固定時
            Mw = np.diag(self.MF[1:])
            Kw = self.upper_K()

        else:
            Mw = self.M
            Kw = self.K0

        w0, _ = self.eig(Mw, Kw)
        C = np.zeros(K.shape)
        for _, w in enumerate(w0):
            C += 2 * self.h * K / w
        return C

    def eig(self, M, K):
        lam, v = LA.eig(np.dot(np.linalg.inv(M), K))
        w = np.sqrt(lam)
        omega = np.sort(w)
        index = np.argsort(w)

        v = normalize_eig(v.T) # 転置の必要あり

        size = len(index)
        vector = np.zeros((size, size))
        for i in range(size):
            vector[i] = v[index[i]]

        return omega, vector

    def update_matrix(self, dis: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        # K更新
        d = np.reshape(dis, self.n_dof)
        for i, ki in enumerate(self.ki):
            d1 = d[ki.n1-1] if ki.n1 != 0 else 0
            di = d[ki.n2-1] - d1

            ki.step(di)
            self.fk[i] = ki.force

        self.K = self.KMatrix()

        # C更新
        if not hasattr(self, 'C') or self.h_type == 1: # 瞬間剛性比例型
            self.C = self.calc_C(self.K)

        return self.M, self.C, self.K, self.I

    def matrix(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.M, self.C, self.K, self.I

    def matrix0(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.M, self.C0, self.K0, self.I
