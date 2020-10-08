import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use('Agg')


def read_csv(file_path):
    try:
        data = pd.read_csv(file_path)
    except:
        data = pd.DataFrame()

    return data


class Plot:

    def __init__(self, analysis):
        self.analysis = analysis
        self.max_df = read_csv(self.analysis.result_data_dir + 'max.csv')
        self.amp_df = read_csv(self.analysis.result_data_dir + 'amp.csv')
        self.th_df = read_csv(self.analysis.result_data_dir + 'time_history.csv')
        self.data_plot_stories = self.analysis.data_plot_stories

    def plot(self, name, x, y, labels="default", title=None, xlabel=None, ylabel=None, xlim_start=None, xlim_end=None, marker=None, top=None, right=None, bottom=None, left=None, figsize=None, plot_dir=None):
        if len(x) != len(y):
            raise ValueError("x,y配列の長さが異なります。")
        fig = plt.figure(figsize=figsize)
        if title:
            plt.title(title)
        if xlabel:
            plt.xlabel(xlabel)
        if ylabel:
            plt.ylabel(ylabel)
        if xlim_start and xlim_end:
            plt.xlim(xlim_start, xlim_end)

        for n in range(len(y)):
            if not labels:
                label = None
            elif labels == "default":
                label = str(n)
            else:
                label = labels[n]

            plt.plot(x[n], y[n], label=label, marker=marker)

        if labels:
            plt.legend()
        plt.gca().set_xlim(right=right, left=left)
        plt.gca().set_ylim(top=top, bottom=bottom)
        plot_dir = plot_dir if plot_dir else self.analysis.result_plot_dir
        fig.savefig(plot_dir + name + '.png', bbox_inches='tight', dpi=100)
        plt.close()

    def wave(self):
        if not self.th_df.empty:
            self.plot('wave', [self.th_df['time']], [self.th_df['acc_00']],
                      title="wave", xlabel="time", ylabel="acc0(m/s2)", figsize=(12, 3))

    def a_acc(self, storey=None):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [
                n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.th_df['time'])
                y.append(self.th_df['a_acc_' + str(n)])

            self.plot('a_acc', x, y, labels=labels, title="absolute acceleration",
                      xlabel="time", ylabel="acc(m/s2)", figsize=(12, 3))

    def acc(self, storey=None):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [
                n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.th_df['time'])
                y.append(self.th_df['acc_' + str(n)])

            self.plot('acc', x, y, labels=labels, title="acceleration",
                      xlabel="time", ylabel="acc(m/s2)", figsize=(12, 3))

    def vel(self, storey=None):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [
                n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.th_df['time'])
                y.append(self.th_df['vel_' + str(n)])

            self.plot('vel', x, y, labels=labels, title="velocity",
                      xlabel="time", ylabel="vel(m/s)", figsize=(12, 3))

    def dis(self, storey=None):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [
                n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.th_df['time'])
                y.append(self.th_df['dis_' + str(n)])

            self.plot('dis', x, y, labels=labels, title="displacement",
                      xlabel="time", ylabel="dis(m)", figsize=(12, 3))

    def cum_dis(self, storey=None):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [
                n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.th_df['time'])
                y.append(self.th_df['cum_dis_' + str(n)])

            self.plot('cum_dis', x, y, labels=labels, title="cum displacement",
                      xlabel="time", ylabel="dis(m)", figsize=(12, 3))

    ### ダンパー周りのPlotは要検討 #######
    def fd(self):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            for n in range(self.analysis.model.n_dof):
                for nn in range(len(self.analysis.dampers[n])):
                    labels.append(str(n) + '_' + str(nn))
                    x.append(self.th_df['time'])
                    y.append(self.th_df['fd_' + str(n) + '_' + str(nn)])

            if self.analysis.max_nd > 0:
                self.plot('fd', x, y, labels=labels, title="damper force",
                          xlabel="time", ylabel="force(kN)", figsize=(12, 3))

    def fs_loop(self):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            for n in range(self.analysis.model.n_dof):
                labels.append(str(n))
                dis0 = self.th_df['dis_' + str(n-1)] if n > 0 else 0
                x.append(self.th_df['dis_' + str(n)] - dis0)
                y.append(self.th_df['fs_' + str(n)])

            self.plot('fs_loop', x, y, labels=labels, title="shear force loop",
                        xlabel="dis.(m)", ylabel="force(kN)", figsize=(8, 8))

    def fd_loop(self):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            for n in range(self.analysis.model.n_dof):
                for nn in range(len(self.analysis.dampers[n])):
                    labels.append(str(n) + '_' + str(nn))

                    if n != 0:
                        x.append(self.th_df['dis_' + str(n)] - self.th_df['dis_' + str(n-1)])
                    else:
                        x.append(self.th_df['dis_' + str(n)])

                    y.append(self.th_df['fd_' + str(n) + '_' + str(nn)])

            if self.analysis.max_nd > 0:
                self.plot('fd_loop', x, y, labels=labels, title="hysteresis loop",
                          xlabel="dis.(m)", ylabel="force(kN)", figsize=(8, 8))

    def fk_loop(self):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            for n in range(self.analysis.model.n_dof):
                for nn in range(len(self.analysis.model.k[n])):
                    labels.append(str(n) + '_' + str(nn))

                    if n != 0:
                        x.append(self.th_df['dis_' + str(n)] - self.th_df['dis_' + str(n-1)])
                    else:
                        x.append(self.th_df['dis_' + str(n)])

                    y.append(self.th_df['fk_' + str(n) + '_' + str(nn)])

            if self.analysis.model.max_nk > 0:
                self.plot('fk_loop', x, y, labels=labels, title="hysteresis loop",
                          xlabel="dis.(m)", ylabel="force(kN)", figsize=(8, 8))

    def a_acc_max(self):
        if not self.max_df.empty:
            self.plot('a_acc_max', [self.max_df['a_acc_max']], [self.max_df['storey']], title="max abs. acceleration",
                      xlabel="max abs. acc(m/s2)", ylabel="storey", marker="o", bottom=0, left=0, figsize=(8, 12))

    def acc_max(self):
        if not self.max_df.empty:
            self.plot('acc_max', [self.max_df['acc_max']], [self.max_df['storey']], title="max acceleration",
                      xlabel="max acc(m/s2)", ylabel="storey", marker="o", bottom=0, left=0, figsize=(8, 12))

    def vel_max(self):
        if not self.max_df.empty:
            self.plot('vel_max', [self.max_df['vel_max']], [self.max_df['storey']], title="max velocity",
                      xlabel="max vel(m/s)", ylabel="storey", marker="o", bottom=0, left=0, figsize=(8, 12))

    def dis_max(self):
        if not self.max_df.empty:
            self.plot('dis_max', [self.max_df['dis_max']], [self.max_df['storey']], title="max displacement",
                      xlabel="max dis(m)", ylabel="storey", marker="o", bottom=0, left=0, figsize=(8, 12))

    def fs_max(self):
        if not self.max_df.empty:
            self.plot('fs_max', [self.max_df['fs_max']], [self.max_df['storey']], title="max shear force",
                      xlabel="max fs(kN)", ylabel="storey", marker="o", bottom=0, left=0, figsize=(8, 12))

    def amp_acc(self, storey=None, xlim_start=0, xlim_end=2):
        if not self.amp_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.amp_df['freq'])
                y.append(self.amp_df['acc_' + str(n)])

            self.plot('amp_acc', x, y, labels=labels, title="acc amp.", xlabel="frequency[Hz]", ylabel="amp(-)", xlim_start=xlim_start, xlim_end=xlim_end)

    def amp_a_acc(self, storey=None, xlim_start=0, xlim_end=2):
        if not self.amp_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.amp_df['freq'])
                y.append(self.amp_df['a_acc_' + str(n)])

            self.plot('amp_a_acc', x, y, labels=labels, title="a_acc amp.", xlabel="frequency[Hz]", ylabel="amp(-)", xlim_start=xlim_start, xlim_end=xlim_end)

    def custom(self):
        if not self.th_df.empty:
            labels = []
            x = []
            y = []
            storey = self.data_plot_stories if self.data_plot_stories else [
                n for n in range(self.analysis.model.n_dof)]
            for n in storey:
                labels.append(str(n))
                x.append(self.th_df['time'])
                y.append(self.th_df['cum_dis_vel_' + str(n)])

            self.plot('cum_dis_vel', x, y, labels=labels, title="cum displacement",
                      xlabel="time", ylabel="dis(m)", figsize=(12, 3))

    def all(self):
        self.wave()
        self.a_acc()
        self.acc()
        self.vel()
        self.dis()
        self.cum_dis()
        self.fd()
        self.fs_loop()
        self.fd_loop()
        self.fk_loop()
        self.a_acc_max()
        self.acc_max()
        self.vel_max()
        self.dis_max()
        self.fs_max()
        self.amp_acc()
        self.amp_a_acc()
        self.custom()
