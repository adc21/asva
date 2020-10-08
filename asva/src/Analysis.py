import copy
import numpy as np
import pandas as pd
from tqdm import tqdm

from asva.src.Damper import Damper
from asva.src.Model import Model
from asva.src.Plot import Plot
from asva.src.Response import Response
from asva.src.Types import ConfigType
from asva.src.utils.config import init_config
from asva.src.utils.calculations import calc_nmb, calc_amplification
from asva.src.utils.time_step import time_step
from asva.src.utils.shear_force import fs_from_fi

class Analysis:
    def __init__(self, config: ConfigType, case: int):
        self.config = init_config(config)
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

        self.result_data_dir = self.config['RESULT_DATA_DIR'][self.case]
        self.result_plot_dir = self.config['RESULT_PLOT_DIR'][self.case]
        self.data_plot_stories = self.config['DATA_PLOT_STORIES']

    def reset(self):
        self.__init__(self.config, self.case) # type: ignore

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
        M, C, K, I = self.damper.amp_matrix()

        wsize = self.config['N_W']
        size = np.size(M, 0)
        self.resp.frequency: np.ndarray = np.array([])
        self.resp.amp_acc = np.zeros((wsize, size))
        self.resp.amp_a_acc = np.zeros((wsize, size))

        for i in range(wsize):
            f = (i+1)*self.config['DF']
            omega = f*2*np.pi

            self.resp.frequency = np.append(self.resp.frequency, f)
            self.resp.amp_acc[i, :] = calc_amplification(M, C, K, I, omega, False)
            self.resp.amp_a_acc[i, :] = calc_amplification(M, C, K, I, omega, True)

        self.amp_done = True

    def print(self):
        if self.th_done:
            print(self.case_name, 'printing...')
            print(self.case_name, 'T0(s)')
            for i, w in enumerate(self.model.w0):
                T = (2 * np.pi) / w
                print(str(i+1), '{0:10.3f}'.format(T))

            print(self.case_name, 'a_acc_max(m/s2)')
            for n in range(self.model.n_dof):
                print(self.model.n_dof - n,
                      '{0:10.3f}'.format(self.resp.a_acc_max[self.model.n_dof - n]))

            print(self.case_name, 'vel_max(m/s)')
            for n in range(self.model.n_dof):
                print(self.model.n_dof - n,
                      '{0:10.3f}'.format(self.resp.vel_max[self.model.n_dof - n]))

            print(self.case_name, 'dis_max(m)')
            for n in range(self.model.n_dof):
                print(self.model.n_dof - n,
                      '{0:10.3f}'.format(self.resp.dis_max[self.model.n_dof - n]))

    def export_result_outline(self):
        path = self.result_data_dir + 'results.txt'

        with open(path, mode='w') as f:
            f.write('解析結果\n\n')
            f.write('--------解析条件--------\n')
            f.write('解析方法 Newmarkβ法')
            f.write('{0:10.3f}\n'.format(self.beta))

            f.write('総質量')
            f.write('{0:10.3f}\n'.format(self.model.Mt))

            f.write('\n\n')
            f.write('--------固有振動数(T(s), f(Hz), w(rad))--------\n')
            for i, w in enumerate(self.model.w0):
                fr = w / (2 * np.pi)
                f.write(str(i+1))
                f.write('{0:10.3f}'.format(1/(fr)))
                f.write('{0:10.3f}'.format(fr))
                f.write('{0:10.3f}\n'.format(w))


            f.write('\n\n')
            f.write('--------固有ベクトル--------\n')
            for i, v0 in enumerate(self.model.v0):
                f.write(f'{i+1}次モード\n')

                f.write('刺激係数')
                f.write('{0:10.3f}\n'.format(self.model.b[i]))

                f.write('有効質量')
                f.write('{0:10.3f}\n'.format(self.model.me[i]))

                f.write('有効質量比')
                f.write('{0:10.3f}\n'.format(self.model.r_me[i]))

                for ii in range(self.model.n_dof):
                    f.write(str(self.model.n_dof-ii))
                    f.write('{0:10.3f}\n'.format(v0[self.model.n_dof-ii-1]))

                f.write('\n')

            f.write('\n\n')
            f.write('--------最大応答値--------\n')
            f.write(f'{self.case_name}\n')
            f.write('最大応答絶対加速度(m/s2)\n')
            for n in range(self.model.n_dof):
                f.write(str(self.model.n_dof - n))
                f.write('{0:10.3f}'.format(self.resp.a_acc_max[self.model.n_dof - n]))
                f.write('\n')

            f.write('最大応答速度(m)\n')
            for n in range(self.model.n_dof):
                f.write(str(self.model.n_dof - n))
                f.write('{0:10.3f}'.format(self.resp.vel_max[self.model.n_dof - n]))
                f.write('\n')

            f.write('最大応答変位(m)\n')
            for n in range(self.model.n_dof):
                f.write(str(self.model.n_dof - n))
                f.write('{0:10.3f}'.format(self.resp.dis_max[self.model.n_dof - n]))
                f.write('\n')

    def export(self):
        print(self.case_name, 'exporting...')
        self.export_result_outline()

        # amplification
        if self.amp_done:
            amp_acc_dict = {}
            amp_a_acc_dict = {}

            for n in range(self.model.n_dof):
                amp_acc_dict['acc_' + str(n)] = self.resp.amp_acc[:, n]
                amp_a_acc_dict['a_acc_' + str(n)] = self.resp.amp_a_acc[:, n]

            amp_base_dict = {
                'freq': self.resp.frequency,
            }

            amp_dict = {**amp_base_dict, **amp_acc_dict, **amp_a_acc_dict}
            amp_df = pd.DataFrame.from_dict(amp_dict)
            amp_df.to_csv(self.result_data_dir + 'amp.csv')

        # time history
        if self.th_done:
            # max
            max_dict = {
                'storey': self.resp.storey,
                'height': self.resp.height,
                'a_acc_max': self.resp.a_acc_max,
                'acc_max': self.resp.acc_max,
                'vel_max': self.resp.vel_max,
                'dis_max': self.resp.dis_max,
                'fu_max': self.resp.fu_max,
                'fs_max': self.resp.fs_max,
            }

            for nn in range(self.max_nd):
                max_dict['fd_max_' + str(nn)] = self.resp.fd_max[:, nn]

            for nn in range(self.model.max_nk):
                max_dict['fk_max_' + str(nn)] = self.resp.fk_max[:, nn]

            max_df = pd.DataFrame.from_dict(max_dict)
            max_df.to_csv(self.result_data_dir + 'max.csv')

            # time history
            th_a_acc_dict = {}
            th_acc_dict = {}
            th_vel_dict = {}
            th_dis_dict = {}
            th_fu_dict = {}
            th_fs_dict = {}
            th_cum_dis_dict = {}
            th_fd_dict = {}
            th_fk_dict = {}
            th_cum_dis_vel_dict = {}

            for n in range(self.model.n_dof):
                th_a_acc_dict['a_acc_' + str(n)] = self.resp.a_acc[:, n]
                th_acc_dict['acc_' + str(n)] = self.resp.acc[:, n]
                th_vel_dict['vel_' + str(n)] = self.resp.vel[:, n]
                th_dis_dict['dis_' + str(n)] = self.resp.dis[:, n]
                th_fu_dict['fu_' + str(n)] = self.resp.fu[:, n]
                th_fs_dict['fs_' + str(n)] = self.resp.fs[:, n]
                th_cum_dis_dict['cum_dis_' + str(n)] = self.resp.cum_dis[:, n]
                th_cum_dis_vel_dict['cum_dis_vel_' + str(n)] = self.resp.cum_dis_vel[:, n]

                for nn in range(len(self.damper.d[n])):
                    th_fd_dict['fd_' + str(n) + '_' + str(nn)] = self.resp.fd[:, n, nn]

                for nn in range(len(self.model.k[n])):
                    th_fk_dict['fk_' + str(n) + '_' + str(nn)] = self.resp.fk[:, n, nn]

            th_base_dict = {
                'time': self.resp.time,
                'acc_00': self.resp.acc_00_res,
            }

            th_dict = {**th_base_dict, **th_a_acc_dict, **th_acc_dict, **th_vel_dict, **th_dis_dict, **th_fu_dict, **th_fs_dict,
                       **th_cum_dis_dict, **th_fd_dict, **th_fk_dict, **th_cum_dis_vel_dict}
            th_df = pd.DataFrame.from_dict(th_dict)
            th_df.to_csv(self.result_data_dir + 'time_history.csv')

    def plot(self):
        print(self.case_name, 'ploting...')
        plot = Plot(self)
        plot.all()
