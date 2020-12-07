"""応答の格納・管理"""
import numpy as np

from asva.utils.wave import read_case_wave, divide_wave, add_wave_required_zero


class Response:
    """応答の格納・管理"""

    def __init__(self, analysis):
        self.analysis = analysis
        self.n_dof_plus_1 = self.analysis.model.n_dof + 1
        self.acc_00_origin = read_case_wave(self.analysis.wave, self.analysis.case_conf)
        acc_00_origin_res = add_wave_required_zero(self.acc_00_origin, self.analysis.resp_end_step)
        self.acc_00_res = acc_00_origin_res[self.analysis.resp_start_step:self.analysis.resp_end_step]
        self.acc_00_ndiv = divide_wave(acc_00_origin_res, self.analysis.n_div)
        self.acc_00 = self.acc_00_ndiv[self.analysis.start_step:self.analysis.end_step]
        self.time = np.arange(self.analysis.resp_n_steps) * self.analysis.dt
        self.a_acc = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.acc = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.vel = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.dis = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.fu = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.rat_fu = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.cum_dis = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.fs = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))
        self.fd = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof, self.analysis.max_nd))
        self.fk = np.zeros((self.analysis.resp_n_steps, len(self.analysis.model.ki)))

        # Custom response
        self.cum_dis_vel = np.zeros((self.analysis.resp_n_steps, self.analysis.model.n_dof))

        # amp
        wsize = self.analysis.amplitude_config['N_W']
        self.frequency: np.ndarray = np.array([])
        self.amp_acc = np.zeros((wsize, self.analysis.model.n_dof))
        self.amp_a_acc = np.zeros((wsize, self.analysis.model.n_dof))

    @property
    def storey(self) -> np.ndarray:
        return np.arange(self.n_dof_plus_1)

    @property
    def acc_00_max(self) -> np.ndarray:
        acc_00_max = np.max(np.abs(self.acc_00_res))
        return acc_00_max

    @property
    def a_acc_max(self) -> np.ndarray:
        a_acc_max = np.zeros((self.n_dof_plus_1))
        for n in range(self.n_dof_plus_1):
            a_acc_max[n] = np.max(np.abs(self.a_acc[:, n-1])) if n != 0 else self.acc_00_max
        return a_acc_max

    @property
    def acc_max(self) -> np.ndarray:
        acc_max = np.zeros((self.n_dof_plus_1))
        for n in range(self.n_dof_plus_1):
            acc_max[n] = np.max(np.abs(self.acc[:, n-1])) if n != 0 else self.acc_00_max
        return acc_max

    @property
    def vel_max(self) -> np.ndarray:
        vel_max = np.zeros((self.n_dof_plus_1))
        for n in range(self.n_dof_plus_1):
            vel_max[n] = np.max(np.abs(self.vel[:, n-1])) if n != 0 else 0
        return vel_max

    @property
    def dis_max(self) -> np.ndarray:
        dis_max = np.zeros((self.n_dof_plus_1))
        for n in range(self.n_dof_plus_1):
            dis_max[n] = np.max(np.abs(self.dis[:, n-1])) if n != 0 else 0
        return dis_max

    @property
    def fu_max(self) -> np.ndarray:
        fu_max = np.zeros((self.n_dof_plus_1))
        for n in range(self.n_dof_plus_1):
            fu_max[n] = np.max(np.abs(self.fu[:, n-1])) if n != 0 else 0
        return fu_max

    @property
    def rat_fu_max(self) -> np.ndarray:
        rat_fu_max = np.zeros((self.n_dof_plus_1))
        for n in range(self.n_dof_plus_1):
            rat_fu_max[n] = np.max(np.abs(self.rat_fu[:, n-1])) if n != 0 else 0
        return rat_fu_max

    @property
    def fs_max(self) -> np.ndarray:
        fs_max = np.zeros((self.n_dof_plus_1))
        for n in range(self.n_dof_plus_1):
            fs_max[n] = np.max(np.abs(self.fs[:, n-1])) if n != 0 else 0
        return fs_max

    @property
    def fd_max(self) -> np.ndarray:
        fd_max = np.zeros((self.n_dof_plus_1, self.analysis.max_nd))
        for n in range(self.n_dof_plus_1):
            for nn in range(self.analysis.max_nd):
                fd_max[n, nn] = np.max(
                    np.abs(self.fd[:, n-1, nn])) if n != 0 else 0
        return fd_max
