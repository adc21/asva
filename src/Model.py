from typing import Tuple, List

import numpy as np
import numpy.linalg as LA

from asva.src.Types import KIType
from asva.src.utils.delta import delta
from asva.src.utils.normalize import normalize_eig
from asva.src.restoring_force import create_restoring_instances, calc_max_nk # check_elastic

class Model:
    def __init__(self, n_dof: int, h: float, h_type: int, height: List[float], MI: List[float], KI: List[List[KIType]], I: List[List[float]], base_isolation: bool = False):
        self.n_dof = n_dof
        self.h = h
        self.h_type = h_type
        self.height = height

        self.max_nk = calc_max_nk(KI)
        self.base_isolation = base_isolation
        self.KI = KI

        self.k = create_restoring_instances(self.n_dof, self.max_nk, self.KI)
        self.fk = np.zeros((self.n_dof, self.max_nk))  # 各層現ステップのダンパー力
        # self.elastic = check_elastic(self.n_dof, self.max_nk, self.KI)

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
            if abs(np.sum(self.vb[:, i]) - 1) > 1e-5:   # 各次数の刺激関数の和が１
                raise ValueError('固有値解析が正しくない可能性があります。')

    def KF(self, D=np.array([]), analysis=False):
        KF = np.zeros((self.n_dof))
        KF_I = np.zeros((self.n_dof, self.max_nk))

        for i in range(self.n_dof):
            D_s = delta(np.reshape(D, self.n_dof)) if len(D) > 0 else D  # 層間変位

            for ii in range(self.max_nk):
                try:
                    _ = self.KI[i][ii]
                except IndexError:
                    continue

                # 弾性
                if not len(D) > 0 or not analysis:
                    KF_I[i, ii] = self.KI[i][ii]["k0"]
                else:
                    KF_I[i, ii] = self.k[i][ii].step(D_s[i])
                    self.fk[i, ii] = self.k[i][ii].force

        KF = np.sum(KF_I, axis=1)
        return KF

    def KMatrix(self, D=np.array([]), analysis=False) -> np.ndarray:
        if not hasattr(self, 'K0') or analysis:
            K = np.zeros((self.n_dof, self.n_dof))
            kf = self.KF(D, analysis)

            if self.n_dof == 1:
                K[0, 0] = kf[0]
            else:
                for n in range(self.n_dof):
                    if n == 0:
                        K[n, n] = kf[n]+kf[n+1]
                        K[n, n+1] = -kf[n+1]
                    elif n == self.n_dof-1:
                        K[n, n-1] = -kf[n]
                        K[n, n] = kf[n]
                    else:
                        K[n, n-1] = -kf[n]
                        K[n, n] = kf[n]+kf[n+1]
                        K[n, n+1] = -kf[n+1]

            if analysis:
                self.K = K

            return K

        else:
            return self.K0

    def upper_K(self):
        """最下層を除いた剛性マトリクス"""
        kf = self.KF()
        K = np.zeros((self.n_dof-1, self.n_dof-1))

        for n in range(self.n_dof-1):
            if n == 0:
                k2 = 0 if self.n_dof-1 == 1 else kf[n+2]
                K[n, n] = kf[n+1]+k2
                if self.n_dof-1 != 1:
                    K[n, n+1] = -k2
            elif n == self.n_dof-2:
                K[n, n-1] = -kf[n+1]
                K[n, n] = kf[n+1]
            else:
                K[n, n-1] = -kf[n+1]
                K[n, n] = kf[n+1]+kf[n+2]
                K[n, n+1] = 0-kf[n+2]

        return K

    def calc_C(self, K):
        if self.base_isolation:
            if self.n_dof == 1:
                C = np.zeros((self.n_dof))
                return C
            else:
                K[0, 0] = self.KF()[1]

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

    def update_C(self) -> np.ndarray:
        # 初期剛性比例型
        if self.h_type == 0:
            if hasattr(self, 'C'):
                return self.C
            else:
                self.C = self.calc_C(self.K0)
                return self.C

        # 瞬間剛性比例型
        elif self.h_type == 1:
            self.C = self.calc_C(self.K)
            return self.C

        else:
            raise ValueError('h_typeの値が正しくありません。')

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

    def update_matrix(self, D=np.array([]), analysis=False) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        self.K = self.KMatrix(D, analysis)
        self.C = self.update_C()
        return self.M, self.C, self.K, self.I

    def matrix(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.M, self.C, self.K, self.I

    def matrix0(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.M, self.C0, self.K0, self.I
