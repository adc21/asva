from asva.src.restoring_force.RestoringForce import RestoringForce

class Bilinear(RestoringForce):
    """BILINEAR バイリニア履歴モデルの負荷経路と内力の算出
    # 引数
    # ep：塑性の判断
    # k0：1次剛性(N/m)
    # k2：２次剛性(N/m)
    # f1：降伏荷重
    # xc,qc：弾性中心の座標
    # dis0：前ステップでの変位
    # q0：前ステップでの復元力
    # dis：1次近似における変位
    # d_dis0：前ステップの変位増分
    # k：瞬間剛性
    # q：現在の内力　
    """

    def __init__(self, k0, a1, f1):
        super().__init__()
        self.k0 = k0
        self.k = self.k0 # 瞬間剛性
        self.a1 = a1
        self.k2 = a1 * self.k0
        self.f1 = f1
        self.dy = self.f1 / self.k0  # 降伏変位
        self.ep = 0
        self.xc = 0
        self.qc = 0
        self.q = 0
        self.q0 = 0

    def step(self, dis) -> float:
        # init
        self.init_step(dis)

        if self.ep == 0:  # 前ステップで弾性領域にいる場合

            # 降伏の判定
            if dis > self.xc + self.dy:  # 引張側で降伏
                self.q = self.qc + self.f1 + self.k2*(dis - (self.xc + self.dy))
                # 弾性中心時のq0　+　降伏時のq　+ 増分復元力分
                self.k = self.k2
                self.ep = 1

            elif dis < self.xc - self.dy:  # 圧縮側で降伏
                self.q = self.qc - self.f1 + self.k2*(dis - (self.xc - self.dy))
                self.k = self.k2
                self.ep = 1

            else:  # 弾性域
                self.q = self.qc + self.k0*(dis - self.xc)
                self.k = self.k0
                self.ep = 0

        elif self.ep == 1:  # 前ステップで塑性領域にいる場合

            # 新たな弾性中心の計算
            if self.d_dis0 > 0:  # 引張側にいる場合
                self.qc = self.q0 - self.f1
                self.xc = self.dis0 - self.dy
            else:  # 圧縮側にいる場合
                self.qc = self.q0 + self.f1
                self.xc = self.dis0 + self.dy

            if self.d_dis * self.d_dis0 > 0:  # 負荷の判定
                if self.d_dis > 0:
                    self.q = self.qc + self.f1 + self.k2 * (dis - (self.xc + self.dy))
                    self.k = self.k2
                    self.ep = 1
                else:
                    self.q = self.qc - self.f1 + self.k2 * (dis - (self.xc - self.dy))
                    self.k = self.k2
                    self.ep = 1

            else:  # 除荷の判定
                self.q = self.qc - self.f1 + self.k0*(dis - (self.xc - self.dy))
                self.k = self.k0
                self.ep = 0

        self.q0 = self.q

        # end
        self.end_step(self.k)
        return self.k
