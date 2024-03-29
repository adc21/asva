from typing import Tuple
import numpy as np


def calc_nmb(F, FD, M: np.ndarray, C: np.ndarray, K: np.ndarray, acc_1, vel_1, dis_1, beta: float, dt: float) -> Tuple[Tuple[float], Tuple[float], Tuple[float]]:
    """
    Newmark β法による加速度・速度・変位マトリクスの計算
    """

    m_bar = M + dt/2*C + beta*dt*dt*K
    f_bar_1 = np.dot(C, (vel_1+dt/2*acc_1))
    f_bar_2 = np.dot(K, (dis_1 + vel_1*dt + (1/2-beta)*acc_1*dt*dt))
    f_bar = F - f_bar_1 - f_bar_2 - FD

    acc_2 = np.dot(np.linalg.inv(m_bar), f_bar)
    vel_2 = vel_1 + (acc_1 + acc_2)*dt/2
    dis_2 = dis_1 + vel_1*dt + (1/2-beta)*acc_1*dt*dt + beta*acc_2*dt*dt
    return acc_2, vel_2, dis_2


def calc_amplitude(M: np.ndarray, C: np.ndarray, K: np.ndarray, I: np.ndarray, omega: float, absolute: bool =False) -> Tuple[float]:
    """
    応答倍率の計算
    """
    size = np.size(M,0)
    a_matrix = (-omega**2*M + 1j*omega*C + K)
    b_matrix = np.dot(M, -I)
    ba_matrix = np.dot(np.linalg.inv(a_matrix), b_matrix)

    if absolute:
        ba_matrix = ba_matrix*-(omega**2) + 1
    else:
        ba_matrix = ba_matrix*-(omega**2)

    amp_value = np.abs(np.reshape(ba_matrix, size))
    return amp_value
