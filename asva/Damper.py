import copy
from typing import Tuple

import numpy as np

from asva.dampers import create_damper_instances
from asva.dampers import iRDT_MATRIX, VDA_MATRIX, VDB_MATRIX, MASS_MATRIX, TMD_MATRIX
from asva.utils.damper import damper_param_along_storeys, add_zeros_to_damper_matrix, damper_exists
from asva.utils.delta import delta

class Damper:
    def __init__(self, analysis):
        self.analysis = analysis
        self.cum_dis = np.zeros((self.analysis.model.n_dof, 1))  # 累積変位
        self.fd_m = np.zeros((self.analysis.model.n_dof, 1))  # ダンパー力マトリクス
        self.d_fd_m = np.zeros((self.analysis.model.n_dof, 1))  # 外力項に加えるダンパー力増分マトリクス

        self.fd0 = np.zeros((self.analysis.model.n_dof, self.analysis.max_nd))  # 各層前ステップのダンパー力
        self.fd = np.zeros((self.analysis.model.n_dof, self.analysis.max_nd))  # 各層現ステップのダンパー力
        self.f0 = np.zeros((self.analysis.model.n_dof, self.analysis.max_nd))  # 各層前ステップのダンパー力（※層間でなく質量に直接作用する）
        self.f = np.zeros((self.analysis.model.n_dof, self.analysis.max_nd))  # 各層現ステップのダンパー力（※層間でなく質量に直接作用する）

        # ダンパー特有の必要パラメータはここで定義
        self.d = create_damper_instances(self.analysis)

        # AI Damper
        self.action = 0

    def update_damper_force_matrix(self, action: int):
        self.action = action
        self.fd = self.damper_force()           # 層間ダンパーのダンパー力計算
        self.f = self.damper_force_to_mass()    # 質点に直接寄与するダンパー力計算
        # print('f', self.fd, self.f)
        d_fd = self.fd - self.fd0
        d_f = self.f - self.f0

        for n in range(self.analysis.model.n_dof):
            if n == self.analysis.model.n_dof-1:
                self.fd_m[n, 0] = np.sum(self.fd[n, :]) - np.sum(self.f[n, :])
                self.d_fd_m[n, 0] = np.sum(d_fd[n, :]) - np.sum(d_f[n, :])
            else:
                self.fd_m[n, 0] = np.sum(self.fd[n, :]) - np.sum(self.fd[n+1, :]) - np.sum(self.f[n, :])
                self.d_fd_m[n, 0] = np.sum(d_fd[n, :]) - np.sum(d_fd[n+1, :]) - np.sum(d_f[n, :])

    def damper_force(self):
        self.fd0 = copy.copy(self.fd)

        for n in range(self.analysis.model.n_dof):
            num_dampers = len(self.analysis.dampers[n])

            # スカラーの層間値に変換
            d_dis = delta(np.reshape(self.analysis.dis, self.analysis.model.n_dof))[n]

            for nn in range(num_dampers):
                # self.fd[n, nn]を返す計算
                try:
                    damper = self.analysis.dampers[n][nn]
                except IndexError:
                    continue

                # Classの場合
                if damper["type"] in ["VDA", "iRDT", "Stopper", "VDB", "MASS"]:
                    self.fd[n, nn] = self.d[n][nn].step(d_dis)

                elif damper["type"] in ["TMD"]:
                    pass

                else:
                    raise ValueError("指定したダンパータイプが正しくありません。")

        return self.fd

    def damper_force_to_mass(self):
        self.f0 = copy.copy(self.f)

        for n in range(self.analysis.model.n_dof):
            num_dampers = len(self.analysis.dampers[n])

            # スカラー値に変換
            # dis_0 = np.asscalar(self.analysis.dis_0[n])
            # vel_0 = np.asscalar(self.analysis.vel_0[n])
            # acc_0 = np.asscalar(self.analysis.acc_0[n])
            # dis = np.asscalar(self.analysis.dis[n])
            # vel = np.asscalar(self.analysis.vel[n])
            a_acc = np.asscalar(self.analysis.a_acc[n])

            for nn in range(num_dampers):
                try:
                    damper = self.analysis.dampers[n][nn]
                except IndexError:
                    continue

                # TMDの場合
                if damper["type"] == "TMD":
                    self.f[n, nn] = self.d[n][nn].step(a_acc)

        return self.f

    def amp_matrix(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        n_dof = self.analysis.model.n_dof

        M, C, K, I = self.analysis.model.matrix0()

        VDB_params = damper_param_along_storeys(n_dof, "VDB", "c1", self.analysis.dampers, True)
        VDA_params = damper_param_along_storeys(n_dof, "VDA", "cd", self.analysis.dampers, True)
        MASS_params = damper_param_along_storeys(n_dof, "MASS", "m", self.analysis.dampers, True)
        TMD_md_params = damper_param_along_storeys(n_dof, "TMD", "md", self.analysis.dampers)
        TMD_cd_params = damper_param_along_storeys(n_dof, "TMD", "cd", self.analysis.dampers)
        TMD_kd_params = damper_param_along_storeys(n_dof, "TMD", "kd", self.analysis.dampers)
        iRDT_md_params = damper_param_along_storeys(n_dof, "iRDT", "md", self.analysis.dampers)
        iRDT_cd_params = damper_param_along_storeys(n_dof, "iRDT", "cd", self.analysis.dampers)
        iRDT_kb_params = damper_param_along_storeys(n_dof, "iRDT", "kb", self.analysis.dampers)


        # 2種類目のiRDTを追加する場合
        # iRDT_md_params2 = np.array([self.analysis.dampers[0][1]['d']['md']])
        # iRDT_cd_params2 = np.array([self.analysis.dampers[0][1]['d']['cd']])
        # iRDT_kb_params2 = np.array([self.analysis.dampers[0][1]['d']['kb']])


        # マトリクスの大きさが変化する場合こちらで計算
        # TMD
        if damper_exists(n_dof, 'TMD', self.analysis.dampers):
            M, C, K, I, TMD_C_matrix, TMD_K_matrix = TMD_MATRIX(n_dof, M, C, K, I, TMD_md_params, TMD_cd_params, TMD_kd_params)
        else:
            TMD_C_matrix, TMD_K_matrix = np.zeros(np.shape(M)), np.zeros(np.shape(M))

        # iRDT
        if damper_exists(n_dof, 'iRDT', self.analysis.dampers):
            M, C, K, I, iRDT_matrix = iRDT_MATRIX(n_dof, M, C, K, I, iRDT_md_params, iRDT_cd_params, iRDT_kb_params)
            # M, C, K, I, iRDT_matrix2 = iRDT_MATRIX(n_dof, M, C, K, I, iRDT_md_params2, iRDT_cd_params2, iRDT_kb_params2)
        else:
            iRDT_matrix = np.zeros(np.shape(M))

        size = np.size(M, 0)

        # マトリクスを拡張する前に計算したダンパーマトリクスにはゼロを追加して拡張し直す
        TMD_C_matrix = add_zeros_to_damper_matrix(TMD_C_matrix, size)
        TMD_K_matrix = add_zeros_to_damper_matrix(TMD_K_matrix, size)
        iRDT_matrix = add_zeros_to_damper_matrix(iRDT_matrix, size)
        # iRDT_matrix2 = add_zeros_to_damper_matrix(iRDT_matrix2, size)

        # マトリクスの大きさが変化しない場合こちらで計算
        VDB_matrix = VDB_MATRIX(n_dof, size, VDB_params)
        VDA_matrix = VDA_MATRIX(n_dof, size, VDA_params)
        MASS_matrix = MASS_MATRIX(n_dof, size, MASS_params)

        # -w**2に比例するもの
        M = M + MASS_matrix

        # 1jwに比例するもの
        C = C + VDB_matrix + VDA_matrix + TMD_C_matrix

        # wに比例しないもの
        K = K + iRDT_matrix + TMD_K_matrix # + iRDT_matrix2

        return M, C, K, I
