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
from asva.Types import AnalysisConfigType, AmplificationConfigType, ExportConfigType, AsvaAmplificationConfigType
from asva.utils.config import init_analysis_config, init_amplification_config, init_export_config
from asva.utils.calculations import calc_nmb, calc_amplification
from asva.utils.time_step import time_step
from asva.utils.shear_force import fs_from_fi

class Analysis:
    def __init__(
            self,
            config: AnalysisConfigType,
            case: int,
            amplification_config: Optional[AmplificationConfigType] = None,
            export_config: Optional[ExportConfigType] = None,
        ):

        self.config = init_analysis_config(config)
        self.amplification_config = init_amplification_config(amplification_config) if amplification_config else None
        self.export_config = init_export_config(self.config, export_config) if export_config else None
        self.case = case
        self.case_conf = self.config['CASES'][self.case]
        self.case_name = self.case_conf['NAME']
        self.wave = self.config['WAVES'][self.case_conf['WAVE']]
        self.amp_done = False
        self.model = Model(self.config['N_DOF'], self.config['H'], self.config['H_TYPE'], self.config['HEIGHT'], self.config['MI'], self.config['KI'], self.config['I'], self.config['BASE_ISOLATION'])
        self.dampers = self.config['DAMPERS'][self.case_conf["DAMPER"]]
        self.n_div, self.dt, self.ddt, self.start_time, self.end_time, self.resp_start_step, self.resp_end_step, self.resp_n_steps, self.start_step, self.end_step, self.n_steps = time_step(self.wave, self.case_conf)
        self.steps = 0  # 試行数
        self.beta = self.config['BETA']
        self.max_nd = self.config['MAX_ND'][self.case]  # 1層あたりのダンパー種類最大数

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
        self.fs = np.zeros((self.model.n_dof, 1))
        self.cum_dis = np.zeros((self.model.n_dof, 1))  # 累積変位
        self.d_a_acc = np.zeros((self.model.n_dof, 1))
        self.d_acc = np.zeros((self.model.n_dof, 1))
        self.d_vel = np.zeros((self.model.n_dof, 1))
        self.d_dis = np.zeros((self.model.n_dof, 1))

        self.d_acc_00 = self.resp.acc_00[0]
        self.f_0 = np.dot(self.model.M, (-1) * self.model.I * self.d_acc_00)  # 外力項
        self.damper = Damper(self)

        self.exporter = Exporter(self)
        self.loader = Loader(self)
        self.plot = Plot(self)

    def reset(self):
        self.__init__(self.config, self.case, self.amplification_config, self.export_config) # type: ignore

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
            self.d_acc_00 = (self.resp.acc_00[t] - self.resp.acc_00[t-1])

        self.d_acc, self.d_vel, self.d_dis = calc_nmb(self.f_0, self.damper.fd_m, self.model.M, self.model.C, self.model.K,
                                                      self.d_acc, self.d_vel, self.d_dis, self.beta,
                                                      self.ddt)

        self.d_a_acc = self.d_acc + self.d_acc_00
        self.acc += self.d_acc
        self.vel += self.d_vel
        self.dis += self.d_dis
        self.a_acc += self.d_a_acc

        Cp = copy.copy(self.model.C)
        Kp = copy.copy(self.model.K)
        self.model.update_matrix(self.dis, analysis=True)

        fu_temp = np.dot((Cp - self.model.C), self.d_vel) + np.dot((Kp - self.model.K), self.d_dis)
        self.f_0 = np.dot(self.model.M, (-1) * self.model.I * self.d_acc_00) + fu_temp
        # with np.errstate(divide='ignore', invalid='ignore'):
        #     UF = np.abs(fu_temp/self.f_0)
        #     MAX_UF = np.nanmax(UF[UF != np.inf])

        self.cum_dis = self.cum_dis + abs(self.d_dis)
        d_fi = np.dot(self.model.K, self.d_dis) + np.dot(self.model.C, self.d_vel)  # 慣性力
        d_fs = fs_from_fi(d_fi)
        self.fs += d_fs
        self.damper.update_damper_force_matrix(action)  # self.damper.fd_mを更新

        if t % n_div == 0:
            rt = t // n_div
            self.resp.a_acc[rt, :] = np.reshape(self.a_acc, n_dof)
            self.resp.acc[rt, :] = np.reshape(self.acc, n_dof)
            self.resp.vel[rt, :] = np.reshape(self.vel, n_dof)
            self.resp.dis[rt, :] = np.reshape(self.dis, n_dof)
            self.resp.fu[rt, :] = np.reshape(fu_temp, n_dof)
            self.resp.cum_dis[rt, :] = np.reshape(self.cum_dis, n_dof)
            self.resp.fs[rt, :] = np.reshape(self.fs, n_dof)
            self.resp.fd[rt, :, :] = self.damper.fd
            self.resp.fk[rt, :, :] = self.model.fk

        self.steps += 1
        return self.reward

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
    def amplification(self):
        if not self.amplification_config:
            raise ValueError('応答倍率の計算には、AmplificationConfigを設定してください。')
        self.amplification_config: AsvaAmplificationConfigType = self.amplification_config # todo: check

        M, C, K, I = self.damper.amp_matrix()

        wsize = self.amplification_config['N_W']
        size = np.size(M, 0)
        self.resp.frequency: np.ndarray = np.array([])
        self.resp.amp_acc = np.zeros((wsize, size))
        self.resp.amp_a_acc = np.zeros((wsize, size))

        for i in range(wsize):
            f = (i+1)*self.amplification_config['DF']
            omega = f*2*np.pi

            self.resp.frequency = np.append(self.resp.frequency, f)
            self.resp.amp_acc[i, :] = calc_amplification(M, C, K, I, omega, False)
            self.resp.amp_a_acc[i, :] = calc_amplification(M, C, K, I, omega, True)

        self.amp_done = True
