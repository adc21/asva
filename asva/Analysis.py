import copy
from typing import Optional

import numpy as np
from tqdm import tqdm

from asva.Exporter import Exporter
from asva.Loader import Loader
from asva.Damper import Damper
from asva.Model import Model
from asva.Plot import Plot
from asva.Response import Response
from asva.Types import AnalysisConfigType, AmplitudeConfigType, ExportConfigType, AsvaAmplitudeConfigType
from asva.utils.config import init_analysis_config, init_amplitude_config, init_export_config
from asva.utils.calculations import calc_nmb, calc_amplitude
from asva.utils.time_step import time_step
from asva.utils.shear_force import fs_from_fi

class Analysis:
    def __init__(
            self,
            config: AnalysisConfigType,
            case: int,
            amplitude_config: Optional[AmplitudeConfigType] = None,
            export_config: Optional[ExportConfigType] = None,
        ):

        self.config = init_analysis_config(config)
        self.amplitude_config = init_amplitude_config(amplitude_config) if amplitude_config else None
        self.export_config = init_export_config(self.config, export_config) if export_config else None
        self.case = case
        self.case_conf = self.config['CASES'][self.case]
        self.case_name = self.case_conf['NAME']
        self.wave = self.config['WAVES'][self.case_conf['WAVE']]
        self.amp_done = False
        self.model = Model(self.config['H'], self.config['H_TYPE'], self.config['MI'], self.config['KI'], self.config['I'], self.config['BASE_ISOLATION'])
        self.dampers = self.config['DAMPERS'][self.case_conf["DAMPER"]]
        self.n_div, self.dt, self.ddt, self.start_time, self.end_time, self.resp_start_step, self.resp_end_step, self.resp_n_steps, self.start_step, self.end_step, self.n_steps = time_step(self.wave, self.case_conf)
        self.steps = 0  # 試行数
        self.beta = self.config['BETA']
        self.max_nd = self.config['MAX_ND'][self.case]  # 1層あたりのダンパー種類最大数

        # for iterations
        """
        self.gamma = 1 / 2
        self.c0 = 1 / (self.beta * self.ddt**2)
        self.c3 = self.gamma / (self.beta * self.ddt)
        """

        self.resp = Response(self)
        self.a_acc_0 = np.zeros((self.model.n_dof, 1))
        self.acc_0 = np.zeros((self.model.n_dof, 1))  # 各層前ステップのダンパー力計算用加速度（※層間ではない）
        self.vel_0 = np.zeros((self.model.n_dof, 1))  # 各層前ステップのダンパー力計算用速度（※層間ではない）
        self.dis_0 = np.zeros((self.model.n_dof, 1))  # 各層前ステップのダンパー力計算用変位（※層間ではない）
        self.a_acc = np.zeros((self.model.n_dof, 1))
        self.acc = np.zeros((self.model.n_dof, 1))
        self.vel = np.zeros((self.model.n_dof, 1))
        self.dis = np.zeros((self.model.n_dof, 1))
        self.fu = np.zeros((self.model.n_dof, 1))
        self.rat_fu = np.zeros((self.model.n_dof, 1))
        self.fi = np.zeros((self.model.n_dof, 1))   # 慣性力
        self.fs = np.zeros((self.model.n_dof, 1))   # 層せん断力
        self.cum_dis = np.zeros((self.model.n_dof, 1))  # 累積変位
        self.d_a_acc = np.zeros((self.model.n_dof, 1))
        self.d_acc = np.zeros((self.model.n_dof, 1))
        self.d_vel = np.zeros((self.model.n_dof, 1))
        self.d_dis = np.zeros((self.model.n_dof, 1))

        self.acc_00 = self.resp.acc_00[0]
        self.d_acc_00 = self.resp.acc_00[0]
        self.f_0 = np.dot(self.model.M, (-1) * self.model.I * self.acc_00)  # 外力項
        self.d_f_0 = np.dot(self.model.M, (-1) * self.model.I * self.d_acc_00)  # 外力項
        self.damper = Damper(self)

        self.exporter = Exporter(self)
        self.loader = Loader(self)
        self.plot = Plot(self)

    def reset(self):
        self.__init__(self.config, self.case, self.amplitude_config, self.export_config) # type: ignore

    # 時刻歴応答解析全ステップの計算
    def analysis(self):
        print(f"{self.case_name} analysing...")

        for _ in tqdm(range(self.n_steps)):
            self.step(None)

    # 時刻歴応答解析１ステップ分の計算
    def step(self, action):
        t = self.steps
        n_dof = self.model.n_dof
        n_div = self.n_div
        self.a_acc_0 = copy.copy(self.a_acc)
        self.acc_0 = copy.copy(self.acc)
        self.vel_0 = copy.copy(self.vel)
        self.dis_0 = copy.copy(self.dis)

        assert(t <= self.n_steps - 1)

        if t != 0:
            self.acc_00 = self.resp.acc_00[t]
            self.d_acc_00 = (self.resp.acc_00[t] - self.resp.acc_00[t-1])

        self.d_f_0 = np.dot(self.model.M, (-1) * self.model.I * self.d_acc_00) - self.fu
        self.d_acc, self.d_vel, self.d_dis = calc_nmb(self.d_f_0, self.damper.d_fd_m, self.model.M, self.model.C, self.model.K,
                                                    self.d_acc, self.d_vel, self.d_dis, self.beta,
                                                    self.ddt)

        self.d_a_acc = self.d_acc + self.d_acc_00
        self.acc += self.d_acc
        self.vel += self.d_vel
        self.dis += self.d_dis
        self.a_acc += self.d_a_acc

        self.model.update_matrix(self.dis) # self.model.C, Kを更新
        self.damper.update_damper_force_matrix(action)  # self.damper.d_fd_mを更新

        self.f_0 = np.dot(self.model.M, (-1) * self.model.I * self.acc_00)
        self.fu = np.dot(self.model.M, self.acc) + np.dot(self.model.C, self.vel) + self.model.Fk + self.damper.fd_m - self.f_0

        # for iterations
        """
        succeed = False
        n_iteration = 0
        while not succeed and n_iteration <= 10:
            if self.fu_is_valid():
                succeed = True
            else:
                Ke = self.model.M * self.c0 + self.model.C * self.c3 + self.model.K + self.damper.fd_m / self.dis

                a_dis = -np.dot(np.linalg.inv(Ke), self.fu)
                a_vel = self.c3 * a_dis
                a_acc = self.c0 * a_dis

                self.d_dis += a_dis
                self.d_vel += a_vel
                self.d_acc += a_acc
                self.d_a_acc = self.d_acc + self.d_acc_00

                self.a_acc = self.a_acc_0 + self.d_a_acc
                self.acc = self.acc_0 + self.d_acc
                self.vel = self.vel_0 + self.d_vel
                self.dis = self.dis_0 + self.d_dis

                self.model.update_matrix(self.dis)
                self.damper.update_damper_force_matrix(action)
                self.fu = np.dot(self.model.M, self.acc) + np.dot(self.model.C, self.vel) + self.model.Fk + self.damper.fd_m - self.f_0

                n_iteration += 1
        """

        self.cum_dis = self.cum_dis + abs(self.d_dis)
        d_fi = np.dot(self.model.K, self.d_dis) + np.dot(self.model.C, self.d_vel)  # 慣性力
        self.fi += d_fi
        d_fs = fs_from_fi(d_fi)
        self.fs += d_fs

        if t % n_div == 0:
            rt = t // n_div
            self.resp.a_acc[rt, :] = np.reshape(self.a_acc, n_dof)
            self.resp.acc[rt, :] = np.reshape(self.acc, n_dof)
            self.resp.vel[rt, :] = np.reshape(self.vel, n_dof)
            self.resp.dis[rt, :] = np.reshape(self.dis, n_dof)
            self.resp.fu[rt, :] = np.reshape(self.fu, n_dof)
            self.resp.rat_fu[rt, :] = np.reshape(self.rat_fu, n_dof)
            self.resp.cum_dis[rt, :] = np.reshape(self.cum_dis, n_dof)
            self.resp.fs[rt, :] = np.reshape(self.fs, n_dof)
            self.resp.fd[rt, :, :] = self.damper.fd
            self.resp.fk[rt, :] = self.model.fk

        self.steps += 1
        return self.reward

    # for iterations
    """
    def fu_is_valid(self):
        # with np.errstate(divide='ignore', invalid='ignore'):
        rat_fu_temp = np.abs(self.fu / self.f_0)
        rat_fu_temp[np.isnan(rat_fu_temp)] = 0
        rat_fu_temp[np.isinf(rat_fu_temp)] = 0

        self.rat_fu = rat_fu_temp
        max_rat_fu = np.max(self.rat_fu)
        valid = max_rat_fu < 0.01
        if not valid:
            print(self.f_0, self.rat_fu)

        return max_rat_fu < 0.1
    """

    # 時刻歴応答解析の終了
    @property
    def th_done(self):
        return self.steps >= self.n_steps - 1

    # AIに与える報酬
    @property
    def reward(self):
        return 1 / (np.max(np.abs(self.a_acc)) + 1e-10)

    # 最大値による報酬の参考値
    @property
    def max_reward(self):
        return 1 / (np.max(np.abs(self.a_acc) + 1e-10))

    # 振動解析の現在の状態
    @property
    def state(self):
        return np.array([self.a_acc, self.acc, self.vel, self.dis, self.a_acc_0, self.acc_0, self.vel_0, self.dis_0, self.d_acc, self.d_vel, self.d_dis], dtype=np.float32) # self.resp.acc_00[self.steps], self.d_acc_00

    # 最大値
    @property
    def max(self):
        return np.array([self.resp.a_acc_max[1], self.resp.vel_max[1], self.resp.dis_max[1], self.resp.fd_max[1]], dtype=np.float32)

    # 応答倍率計算
    def amplitude(self):
        if not self.amplitude_config:
            raise ValueError('応答倍率の計算には、AmplitudeConfigを設定してください。')
        self.amplitude_config: AsvaAmplitudeConfigType = self.amplitude_config # todo: check

        M, C, K, I = self.damper.amp_matrix()

        wsize = self.amplitude_config['N_W']
        size = np.size(M, 0)

        self.model.amp_size = size
        self.resp.amp_acc = np.zeros((wsize, size))
        self.resp.amp_a_acc = np.zeros((wsize, size))

        for i in range(wsize):
            f = (i+1)*self.amplitude_config['DF']
            omega = f*2*np.pi

            self.resp.frequency = np.append(self.resp.frequency, f)
            self.resp.amp_acc[i, :] = calc_amplitude(M, C, K, I, omega, False)
            self.resp.amp_a_acc[i, :] = calc_amplitude(M, C, K, I, omega, True)

        self.amp_done = True
