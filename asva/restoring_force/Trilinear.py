from asva.restoring_force.RestoringForce import RestoringForce


class Trilinear(RestoringForce):
    def __init__(self, n1: int, n2: int, k0: float, a1: float, a2: float, fy1: float, fy2: float):
        super().__init__(n1, n2, k0)
        self.state = 0     # 状態

        self.a1 = a1
        self.a2 = a2
        self.fy1 = fy1
        self.fy2 = fy2
        self.disy1 = self.fy1 / self.k0
        self.disy2 = self.fy1 / self.k0 + (self.fy2-self.fy1) / self.a1 / self.k0

        self.k = self.k0    # 瞬間剛性
        self.b = 0          # 切片荷重

        self.dis_l = -self.disy1  # 最小値
        self.dis_r = self.disy1   # 最大値

    def step(self, dis: float) -> float:
        # init
        self.init_step(dis)

        if self.state == 0:
            self.trilinear_0()

        elif self.state == 1:
            self.trilinear_1()

        elif self.state == 2:
            self.trilinear_2()

        elif self.state == 3:
            self.trilinear_3()

        elif self.state == 4:
            self.trilinear_4()

        # end
        self.end_step(self.k)
        return self.k

    def trilinear_0(self):

        if self.dis < self.dis_l:
            y_ = self.k * self.dis_l + self.b
            self.k = self.a1 * self.k0
            self.b = y_ - self.a1 * self.k0 * self.dis_l
            self.dis_l = self.dis
            self.state = 2
            #  0 -> 2
            y_ = self.k * self.dis + self.b
            if y_ <= self.a2 * self.k0 * self.dis - self.fy2 + self.a2 * self.k0 * self.disy2:

                self.k = self.a2 * self.k0
                self.b = -self.fy2 + self.k * self.disy2
                self.state = 4
                #  0 -> 4
                return

            return

        if self.dis > self.dis_r:
            y_ = self.k * self.dis_r + self.b
            self.k = self.a1 * self.k0
            self.b = y_ - self.k * self.dis_r
            self.dis_r = self.dis
            self.state = 1
            #  0 -> 1
            y_ = self.k * self.dis + self.b
            if y_ >= self.a2 * self.k0 * self.dis + self.fy2 - self.a2 * self.k0 * self.disy2:

                self.k = self.a2 * self.k0
                self.b = self.fy2 - self.k * self.disy2
                self.state = 3
                #  0 -> 3
                return

            return

        return

    def trilinear_1(self):

        y_ = self.k * self.dis + self.b
        if y_ >= self.a2 * self.k0 * self.dis + self.fy2 - self.a2 * self.k0 * self.disy2:

            self.k = self.a2 * self.k0
            self.b = self.fy2 - self.k * self.disy2
            self.dis_r = self.dis
            self.state = 3

            return
            #  1 -> 3

        if self.dis < self.dis_r:

            y_ = self.k * self.dis_r + self.b
            self.k = self.k0
            self.b = y_ - self.k * self.dis_r
            self.dis_l = self.dis_r - 2 * self.disy1
            self.state = 0

            return
            #  1 -> 0

        self.dis_r = self.dis
        return
        #  1 -> 1

    def trilinear_2(self):

        y_ = self.k * self.dis + self.b
        if y_ <= self.a2 * self.k0 * self.dis - self.fy2 + self.a2 * self.k0 * self.disy2:

            self.k = self.a2 * self.k0
            self.b = -self.fy2 + self.k * self.disy2
            self.dis_l = self.dis
            self.state = 4

            return
            #  2 -> 4

        if self.dis > self.dis_l:

            y_ = self.k * self.dis_l + self.b
            self.k = self.k0
            self.b = y_ - self.k * self.dis_l
            self.dis_r = self.dis_l + 2 * self.disy1
            self.state = 0

            return
            #  2 -> 0

        self.dis_l = self.dis
        return
        #  2 -> 2

    def trilinear_3(self):

        if self.dis < self.dis_r:

            y_ = self.k * self.dis_r + self.b
            self.k = self.k0
            self.b = y_ - self.k * self.dis_r
            self.dis_l = self.dis_r - 2 * self.disy1
            self.state = 0

            return
            #  3 -> 0

        self.dis_r = self.dis
        return
        #  3 -> 3

    def trilinear_4(self):

        if self.dis > self.dis_l:

            y_ = self.k * self.dis_l + self.b
            self.k = self.k0
            self.b = y_ - self.k * self.dis_l
            self.dis_r = self.dis_l + 2 * self.disy1
            self.state = 0

            return
            #  4 -> 0

        self.dis_l = self.dis
        return
        #  4 -> 4
