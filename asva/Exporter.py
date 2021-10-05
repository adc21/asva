import numpy as np
import pandas as pd

class Exporter:
    def __init__(self, analysis):
        self.analysis = analysis
        self.result_data_dir = self.analysis.export_config['RESULT_DATA_DIR'][self.analysis.case] if self.analysis.export_config else None
        self.result_plot_dir = self.analysis.export_config['RESULT_PLOT_DIR'][self.analysis.case] if self.analysis.export_config else None
        self.data_plot_stories = self.analysis.export_config['DATA_PLOT_STORIES'] if self.analysis.export_config else None

    def print(self):
        if self.analysis.th_done:
            print(self.analysis.case_name, 'printing...')
            print(self.analysis.case_name, 'T0(s)')
            for i, w in enumerate(self.analysis.model.w0):
                T = (2 * np.pi) / w
                print(str(i+1), '{0:10.3f}'.format(T))

            print(self.analysis.case_name, 'a_acc_max(m/s2)')
            for n in range(self.analysis.model.n_dof):
                print(self.analysis.model.n_dof - n,
                      '{0:10.3f}'.format(self.analysis.resp.a_acc_max[self.analysis.model.n_dof - n]))

            print(self.analysis.case_name, 'vel_max(m/s)')
            for n in range(self.analysis.model.n_dof):
                print(self.analysis.model.n_dof - n,
                      '{0:10.3f}'.format(self.analysis.resp.vel_max[self.analysis.model.n_dof - n]))

            print(self.analysis.case_name, 'dis_max(m)')
            for n in range(self.analysis.model.n_dof):
                print(self.analysis.model.n_dof - n,
                      '{0:10.3f}'.format(self.analysis.resp.dis_max[self.analysis.model.n_dof - n]))

            """
            print(self.analysis.case_name, 'fu_max(kN)')
            for n in range(self.analysis.model.n_dof):
                print(self.analysis.model.n_dof - n,
                      '{0:10.3f}'.format(self.analysis.resp.fu_max[self.analysis.model.n_dof - n]))

            print(self.analysis.case_name, 'rat_fu_max(%)')
            for n in range(self.analysis.model.n_dof):
                print(self.analysis.model.n_dof - n,
                      '{0:10.1f}'.format(self.analysis.resp.rat_fu_max[self.analysis.model.n_dof - n] * 100))
            """

    def export_result_outline(self):
        if not self.result_data_dir:
            raise ValueError('ExportConfigが設定されていません。')

        path = self.result_data_dir + 'results.txt'

        with open(path, mode='w') as f:
            f.write('解析結果\n\n')
            f.write('--------解析条件--------\n')
            f.write('解析方法 Newmarkβ法')
            f.write('{0:10.3f}\n'.format(self.analysis.beta))

            f.write('総質量')
            f.write('{0:10.3f}\n'.format(self.analysis.model.Mt))

            f.write('\n\n')
            f.write('--------固有振動数(T(s), f(Hz), w(rad))--------\n')
            for i, w in enumerate(self.analysis.model.w0):
                fr = w / (2 * np.pi)
                f.write(str(i+1))
                f.write('{0:10.3f}'.format(1/(fr)))
                f.write('{0:10.3f}'.format(fr))
                f.write('{0:10.3f}\n'.format(w))


            f.write('\n\n')
            f.write('--------固有ベクトル--------\n')
            for i, v0 in enumerate(self.analysis.model.v0):
                f.write(f'{i+1}次モード\n')

                f.write('刺激係数')
                f.write('{0:10.3f}\n'.format(self.analysis.model.b[i]))

                f.write('有効質量')
                f.write('{0:10.3f}\n'.format(self.analysis.model.me[i]))

                f.write('有効質量比')
                f.write('{0:10.3f}\n'.format(self.analysis.model.r_me[i]))

                for ii in range(self.analysis.model.n_dof):
                    f.write(str(self.analysis.model.n_dof-ii))
                    f.write('{0:10.3f}\n'.format(v0[self.analysis.model.n_dof-ii-1]))

                f.write('\n')

            f.write('\n\n')
            f.write('--------最大応答値--------\n')
            f.write(f'{self.analysis.case_name}\n')
            f.write('最大応答絶対加速度(m/s2)\n')
            for n in range(self.analysis.model.n_dof):
                f.write(str(self.analysis.model.n_dof - n))
                f.write('{0:10.3f}'.format(self.analysis.resp.a_acc_max[self.analysis.model.n_dof - n]))
                f.write('\n')

            f.write('最大応答速度(m)\n')
            for n in range(self.analysis.model.n_dof):
                f.write(str(self.analysis.model.n_dof - n))
                f.write('{0:10.3f}'.format(self.analysis.resp.vel_max[self.analysis.model.n_dof - n]))
                f.write('\n')

            f.write('最大応答変位(m)\n')
            for n in range(self.analysis.model.n_dof):
                f.write(str(self.analysis.model.n_dof - n))
                f.write('{0:10.3f}'.format(self.analysis.resp.dis_max[self.analysis.model.n_dof - n]))
                f.write('\n')

    def export(self):
        if not self.result_data_dir:
            raise ValueError('ExportConfigが設定されていません。')

        print(self.analysis.case_name, 'exporting...')
        self.export_result_outline()

        # amplitude
        if self.analysis.amp_done:
            amp_acc_dict = {}
            amp_a_acc_dict = {}

            for n in range(self.analysis.model.amp_size):
                amp_acc_dict['acc_' + str(n)] = self.analysis.resp.amp_acc[:, n]
                amp_a_acc_dict['a_acc_' + str(n)] = self.analysis.resp.amp_a_acc[:, n]

            amp_base_dict = {
                'freq': self.analysis.resp.frequency,
            }

            amp_dict = {**amp_base_dict, **amp_acc_dict, **amp_a_acc_dict}
            amp_df = pd.DataFrame.from_dict(amp_dict)
            amp_df.to_csv(self.result_data_dir + 'amp.csv')
            self.analysis.loader.load_amp()

        # time history
        if self.analysis.th_done:
            # max
            max_dict = {
                'storey': self.analysis.resp.storey,
                'a_acc_max': self.analysis.resp.a_acc_max,
                'acc_max': self.analysis.resp.acc_max,
                'vel_max': self.analysis.resp.vel_max,
                'dis_max': self.analysis.resp.dis_max,
                'fu_max': self.analysis.resp.fu_max,
                'fs_max': self.analysis.resp.fs_max,
            }

            for nn in range(self.analysis.max_nd):
                max_dict['fd_max_' + str(nn)] = self.analysis.resp.fd_max[:, nn]

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

            for n in range(self.analysis.model.n_dof):
                th_a_acc_dict['a_acc_' + str(n)] = self.analysis.resp.a_acc[:, n]
                th_acc_dict['acc_' + str(n)] = self.analysis.resp.acc[:, n]
                th_vel_dict['vel_' + str(n)] = self.analysis.resp.vel[:, n]
                th_dis_dict['dis_' + str(n)] = self.analysis.resp.dis[:, n]
                th_fu_dict['fu_' + str(n)] = self.analysis.resp.fu[:, n]
                th_fs_dict['fs_' + str(n)] = self.analysis.resp.fs[:, n]
                th_cum_dis_dict['cum_dis_' + str(n)] = self.analysis.resp.cum_dis[:, n]
                th_cum_dis_vel_dict['cum_dis_vel_' + str(n)] = self.analysis.resp.cum_dis_vel[:, n]

                for nn in range(len(self.analysis.damper.d[n])):
                    th_fd_dict['fd_' + str(n) + '_' + str(nn)] = self.analysis.resp.fd[:, n, nn]

                for nn, _ in enumerate(self.analysis.model.ki):
                    th_fk_dict['fk_' + str(nn)] = self.analysis.resp.fk[:, nn]

            th_base_dict = {
                'time': self.analysis.resp.time,
                'acc_00': self.analysis.resp.acc_00_res,
            }

            th_dict = {**th_base_dict, **th_a_acc_dict, **th_acc_dict, **th_vel_dict, **th_dis_dict, **th_fu_dict, **th_fs_dict,
                       **th_cum_dis_dict, **th_fd_dict, **th_fk_dict, **th_cum_dis_vel_dict}
            th_df = pd.DataFrame.from_dict(th_dict)
            th_df.to_csv(self.result_data_dir + 'time_history.csv')
            self.analysis.loader.load_th()
