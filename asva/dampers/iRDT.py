"""iRDT"""
from typing import Tuple, TypedDict
import copy
import numpy as np
from asva.dampers.Damper import Damper

class iRDTType(TypedDict):
    md: float
    cd: float
    alpha: float
    kb: float
    fr: float
    cosA: float

# ===================================================================
# iRDT の抵抗力(2) 改訂
# SUBROUTINE RdtCL2
# ===================================================================
# ----- Input -----
# CC# CV^a 型の減衰係数(kN/kine)
# alpha CV^a 型の非線形乗数
# md 回転慣性による等価質量(kN･s2/cm)
# AN1 軸加速度(cm/s2)
# VN1 軸速度(cm/s)
# ----- Output -----
# PN 全抵抗力Pn(kN)
# QV 減衰特性CV^a 型の軸方向力(kN)
# QI 等価質量による軸方向力(kN)

# -----
# CEN CV^a 型に関する等価減衰係数(kN/kine)
# CT CV^a 型に関する等価接線減衰係数(kN/kine)
# ----- Work -----
# VN11 減衰係数計算用の速度
# ======================================================================


def iRDT2(cd, alpha, md, AN1, VN1):

    if (abs(VN1) > 0.001):
        VN11 = abs(VN1)
        CEN = cd*(VN11**(alpha-1.0))
        CT = cd*alpha*(VN11**(alpha-1.0))
    else:
        VN11 = 0.001
        CEN = cd*(VN11**(alpha-1.0))
        CT = cd*(VN11**(alpha-1.0))

    # ----粘性抵抗力による軸方向力
    QV = cd*(VN11**(alpha-1.0))*VN1
    # ----慣性力による軸方向力Qi
    QI = md*AN1
    # ----全抵抗力Pn
    PN = QV+QI
    # ----
    # CEN=cd*(VN11**(alpha-1.0))
    # CT=cd*alpha*(VN11**(alpha-1.0))
    # ----
    return PN, QV, QI, CEN, CT


class iRDT(Damper):
    def __init__(self, dt: float, Nd: float, md: float, cd: float, alpha: float, kb: float, fr: float, cosA: float):
        super().__init__(dt, Nd)
        self.md = md * self.Nd
        self.cd = cd * self.Nd
        self.me = self.md
        self.ce = self.cd
        self.alpha = alpha
        self.kb = kb * self.Nd
        self.fr = fr * self.Nd
        self.cosA = cosA

        self.acc_b: float = 0
        self.vel_b: float = 0
        self.dis_b: float = 0
        self.acc_b0: float = 0
        self.vel_b0: float = 0
        self.dis_b0: float = 0
        self.PN: float = 0
        self.force: float = 0

    def step(self, dis: float):
        # init
        self.init_step(dis)

        AZK = 0.0000000001
        KB = self.kb*self.cosA*self.cosA

        # ----KB の評価係数(支持部材降伏モデル)
        CD = self.ce+2*self.me/self.dt
        if (abs(self.PN) <= self.fr):
            AL = 1+2*CD/self.dt/KB
        elif((self.PN > self.fr) and ((CD*(self.vel-self.vel0)+2*CD*self.vel_b0-2*self.me*(self.acc0-self.acc_b0)) > 0.0)):
            AL = 1+2*CD/self.dt/AZK
        elif((self.PN > self.fr) and ((CD*(self.vel-self.vel0)+2*CD*self.vel_b0-2*self.me*(self.acc0-self.acc_b0)) <= 0.0)):
            AL = 1+2*CD/self.dt/KB
        elif((self.PN < -self.fr) and ((CD*(self.vel-self.vel0)+2*CD*self.vel_b0-2*self.me*(self.acc0-self.acc_b0)) < 0.0)):
            AL = 1+2*CD/self.dt/AZK
        else:
            AL = 1+2*CD/self.dt/KB

        # ----iRDT の水平力増分
        DP = (CD*(self.vel-self.vel0)+2*CD*self.vel_b0-2*self.me*(self.acc0-self.acc_b0))/AL
        # ----KB の加速度･速度･変位(支持部材降伏モデル)
        d_dis_b: float = 0
        if (abs(self.PN) <= self.fr):
            d_dis_b = DP/KB
        elif ((self.PN > self.fr) and (DP > 0.0)):
            d_dis_b = DP/AZK
        elif ((self.PN > self.fr) and (DP <= 0.0)):
            d_dis_b = DP/KB
        elif ((self.PN < -self.fr) and (DP < 0.0)):
            d_dis_b = DP/AZK
        else:
            d_dis_b = DP/KB

        self.dis_b = d_dis_b+self.dis_b0
        self.vel_b = 2*d_dis_b/self.dt-self.vel_b0
        self.acc_b = 4*d_dis_b/self.dt/self.dt-4*self.vel_b0/self.dt-self.acc_b0

        # ----iRDT の軸方向の加速度･速度･変位
        # DN0=(Dd0-self.dis_b0)*self.cosA
        AN1 = (self.acc-self.acc_b)*self.cosA
        VN1 = (self.vel-self.vel_b)*self.cosA
        # DN1=(Dd-self.dis_b)*self.cosA
        # ----iRDT の軸方向の力･接線減衰など(1 基あたり)
        self.PN, QV, QI, CEN, CT = iRDT2(self.cd, self.alpha, self.md, AN1, VN1)
        # ----iRDT の水平方向の接線減衰など
        self.ce = CT*self.cosA*self.cosA
        self.me = self.md*self.cosA*self.cosA

        # ----水平力
        self.force = (CEN*VN1+self.md*AN1)*self.cosA

        # ----前ｽﾃｯﾌﾟの支持剛性の加速度･速度･変位
        self.acc_b0 = copy.copy(self.acc_b)
        self.vel_b0 = copy.copy(self.vel_b)
        self.dis_b0 = copy.copy(self.dis_b)

        # end
        self.end_step()
        return self.force

def iRDT_MATRIX(n_dof: int, M: np.ndarray, C: np.ndarray, K: np.ndarray, I: np.ndarray, MD: np.ndarray, CD: np.ndarray, KD: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """応答倍率計算時のダンパーマトリクス（MD,CD,KDの値は１層あたり１種類のみとすること）"""
    assert MD.size == n_dof, f"MD size must be same as n_dof ${n_dof}"

    size = np.size(M,0)
    matrix_size = size + n_dof

    MATRIX = np.zeros((matrix_size, matrix_size))
    M2 = np.concatenate((np.concatenate((M, np.zeros((n_dof, size)))), np.concatenate((np.zeros((size, n_dof)), np.diag(MD)))), axis=1)
    C2 = np.concatenate((np.concatenate((C, np.zeros((n_dof, size)))), np.concatenate((np.zeros((size, n_dof)), np.diag(CD)))), axis=1)
    K2 = np.concatenate((np.concatenate((K, np.zeros((n_dof, size)))), np.concatenate((np.zeros((size, n_dof)), np.zeros((n_dof, n_dof))))), axis=1)
    I2 = np.concatenate((I, np.zeros((n_dof, 1))))

    if n_dof == 1:
        MATRIX[0, 0] = KD[0]

        MATRIX[0, size] = -KD[0]
        MATRIX[size, size] = KD[0]
        MATRIX[size, 0] = -KD[0]
    else:
        for n in range(n_dof):
            if n == 0:
                MATRIX[0, 0] = KD[0]+KD[1]
                MATRIX[0, 1] = -KD[1]
            elif n == n_dof-1:
                MATRIX[n, n-1] = -KD[n]
                MATRIX[n, n] = KD[n]
            else:
                MATRIX[n, n-1] = -KD[n]
                MATRIX[n, n] = KD[n]+KD[n+1]
                MATRIX[n, n+1] = -KD[n+1]

            if n ==0:
                MATRIX[0, n_dof] = -KD[0]
                MATRIX[n_dof, n_dof] = KD[0]
                MATRIX[n_dof, 0] = -KD[0]
            else:
                MATRIX[n-1, n_dof+n] = KD[n]
                MATRIX[n, n_dof+n] = -KD[n]
                MATRIX[n_dof+n, n_dof+n] = KD[n]
                MATRIX[n_dof+n, n-1] = KD[n]
                MATRIX[n_dof+n, n] = -KD[n]

    return M2, C2, K2, I2, MATRIX
