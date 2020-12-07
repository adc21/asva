from asva.restoring_force.RestoringForce import RestoringForce


class Takeda(RestoringForce):
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
        self.b = 0         # 切片荷重

        self.dis_l1 = -self.disy1  # 最小値
        self.dis_l2 = -1e10
        self.dis_l3 = -1e10
        self.kl = self.k0
        self.fly = self.k * self.dis + self.b
        self.dis_r1 = self.disy1   # 最大値
        self.dis_r2 = 1e10
        self.dis_r3 = 1e10
        self.kr = self.k0
        self.fry = self.k * self.dis + self.b
        self.gamma = 0.4        # γ
        self.kp = (self.fy1 + self.fy2) / (self.disy1 + self.disy2)

    def step(self, dis: float) -> None:
        # init
        self.init_step(dis)

        if self.state == 0:
            self.takeda_0()
        elif self.state == 1:
            self.takeda_1()
        elif self.state == 2:
            self.takeda_2()
        elif self.state == 3:
            self.takeda_3()
        elif self.state == 4:
            self.takeda_4()
        elif self.state == 5:
            self.takeda_5()
        elif self.state == 6:
            self.takeda_6()
        elif self.state == 7:
            self.takeda_7()
        elif self.state == 8:
            self.takeda_8()
        elif self.state == 9:
            self.takeda_9()
        elif self.state == 10:
            self.takeda_10()
        elif self.state == 11:
            self.takeda_11()
        elif self.state == 12:
            self.takeda_12()
        elif self.state == 13:
            self.takeda_13()
        elif self.state == 14:
            self.takeda_14()
        elif self.state == 15:
            self.takeda_15()
        elif self.state == 16:
            self.takeda_16()
        elif self.state == 17:
            self.takeda_17()
        elif self.state == 18:
            self.takeda_18()
        elif self.state == 19:
            self.takeda_19()
        elif self.state == 20:
            self.takeda_20()
        elif self.state == 21:
            self.takeda_21()
        elif self.state == 22:
            self.takeda_22()
        elif self.state == 23:
            self.takeda_23()
        elif self.state == 24:
            self.takeda_24()
        elif self.state == 25:
            self.takeda_25()
        elif self.state == 26:
            self.takeda_26()
        elif self.state == 27:
            self.takeda_27()
        elif self.state == 28:
            self.takeda_28()
        elif self.state == 29:
            self.takeda_29()
        elif self.state == 30:
            self.takeda_30()

        # end
        self.end_step(self.k)

    def takeda_0(self):
        if self.dis < -self.disy1:
            self.k = self.a1*self.k0
            self.b = -self.fy1 + self.a1*self.fy1
            self.dis_l1 = self.dis
            self.state = 2  # 0->2

        if self.dis > self.disy1:
            self.k = self.a1*self.k0
            self.b = self.fy1 - self.a1*self.fy1
            self.dis_r1 = self.dis
            self.state = 1  # 0->1

        return

    def takeda_1(self):
        if self.dis > self.disy2:
            self.k = self.a2*self.k0
            self.b = self.fy2 - self.a2*self.k0*self.disy2
            self.state = 7
            self.kr = self.kp
            self.kl = self.kp
            return  # 1->7

        if self.dis < self.dis0:
            self.dis_r1 = self.dis0
            y_ = self.k*self.dis0 + self.b
            self.k = (y_+self.fy1) / (self.dis_r1+self.disy1)
            self.b = -self.fy1 + self.k*self.disy1
            self.kr = self.k
            self.state = 3  # 1->3

        return  # 1->1

    def takeda_2(self):
        if self.dis < -self.disy2:
            self.k = self.a2*self.k0
            self.b = -self.fy2 + self.a2*self.k0*self.disy2
            self.state = 8
            self.kr = self.kp
            self.kl = self.kp
            return  # 2->8

        if self.dis > self.dis0:
            self.dis_l1 = self.dis0
            y_ = self.k*self.dis0 + self.b
            self.k = (self.fy1 - y_) / (self.disy1 - self.dis_l1)
            self.b = self.fy1-self.k*self.disy1
            self.kl = self.k
            self.state = 4  # 2->4

        return  # 2->2

    def takeda_3(self):
        y_ = self.k*self.dis+self.b
        if y_ < 0:
            x_ = -self.b/self.k
            y_ = self.a1*self.k0*self.dis_l1 - self.fy1+self.a1*self.fy1
            self.k = (-y_)/(x_-self.dis_l1)
            self.b = -self.k*x_
            self.state = 5     # 3->5
            self.dis_r2 = 1e10

        if self.dis_r2 < self.dis:
            y_ = self.k*self.dis_r2+self.b
            self.k = (self.a1*self.k0*self.dis_r1+self.fy1-self.a1*self.fy1-y_)/(self.dis_r1-self.dis_r2)
            self.b = y_ - self.k*self.dis_r2
            self.dis_r2 = 1e10
            self.state = 6  # 3->6

        if y_ > self.a1*self.k0*self.dis+self.fy1-self.a1*self.fy1:
            self.k = self.a1*self.k0
            self.b = self.fy1-self.k*self.disy1
            self.dis_r1 = self.dis
            self.state = 1  # 3->1

        return

    def takeda_4(self):

        y_ = self.k*self.dis+self.b
        if y_ > 0:
            x_ = -self.b/self.k
            y_ = self.a1*self.k0*self.dis_r1+self.fy1-self.a1*self.fy1
            self.k = (-y_)/(x_-self.dis_r1)
            self.b = -self.k*x_
            self.state = 6  # 4->6
            self.dis_l2 = -1e10

        if self.dis < self.dis_l2:
            y_ = self.k*self.dis_l2+self.b
            self.k = (self.a1*self.k0*self.dis_l1-self.fy1+self.a1*self.fy1-y_)/(self.dis_l1-self.dis_l2)
            self.b = y_-self.k*self.dis_l2
            self.dis_l2 = -1e10
            self.state = 5  # 4->5

        if y_ < self.a1*self.k0*self.dis-self.fy1+self.a1*self.fy1:
            self.k = self.a1*self.k0
            self.b = -self.fy1+self.k*self.disy1
            self.dis_l1 = self.dis
            self.state = 2  # 4->2

        return

    def takeda_5(self):

        if self.dis < self.dis_l1:
            self.k = self.a1*self.k0
            self.b = -self.fy1+self.a1*self.fy1
            self.dis_l1 = self.dis
            self.state = 2
            return  # 5->2

        if self.dis0 < self.dis:
            y_ = self.k*self.dis0+self.b
            self.k = self.kl
            self.b = y_-self.k*self.dis0
            self.dis_l2 = self.dis0
            self.state = 4  # 5->4
            return

        return  # 5->5

    def takeda_6(self):

        if self.dis > self.dis_r1:
            self.k = self.a1*self.k0
            self.b = self.fy1-self.a1*self.fy1
            self.dis_r1 = self.dis
            self.state = 1
            return  # 6->1

        if self.dis0 > self.dis:
            y_ = self.k*self.dis0+self.b
            self.k = self.kr
            self.b = y_-self.k*self.dis0
            self.dis_r2 = self.dis0
            self.state = 3
            return  # 6->3

        return  # 6->6

    def takeda_7(self):

        if self.dis0 <= self.dis:
            return  # 7->7

        y_ = self.k*self.dis0+self.b
        self.dis_r1 = self.dis0
        self.k = self.kp * pow((abs(self.dis_r1 / self.disy2)), -self.gamma)
        self.kr = self.k
        self.b = y_-self.k*self.dis0
        self.dis_r2 = 1e10
        self.dis_l2 = -1e10
        if self.dis_l1 == -self.disy1:
            self.state = 17
            return  # 7->17

        self.state = 9
        return  # 7->9

    def takeda_8(self):

        if self.dis0 >= self.dis:
            return  # 8->8

        if self.dis0 < self.dis:
            y_ = self.k*self.dis0+self.b
            self.dis_l1 = self.dis0
            self.k = self.kp*pow((abs(self.dis_l1 / self.disy2)), -self.gamma)
            self.kl = self.k
            self.b = y_-self.k*self.dis0
            self.dis_r2 = 1e10
            self.dis_l2 = -1e10

        if self.dis_r1 == self.disy1:
            self.state = 18
            return  # 8->18

        self.state = 10
        return  # 8->10

    def takeda_9(self):

        if self.dis > self.dis_r2:
            y_ = self.k*self.dis_r2+self.b
            self.k = (self.a2*self.k0*self.dis_r1+self.fy2-self.a2*self.k0*self.disy2-y_)/(self.dis_r1-self.dis_r2)
            self.b = y_-self.k*self.dis_r2
            self.dis_r2 = 1e10
            self.state = 12
            return  # 9->12

        y_ = self.k*self.dis+self.b
        if y_ > self.a2*self.k0*self.dis+self.fy2-self.a2*self.k0*self.disy2:
            self.k = self.a2*self.k0
            self.b = self.fy2-self.a2*self.k0*self.disy2
            self.state = 7
            return  # 9->7

        if y_ > 0:
            return  # 9->9

        x_ = -self.b/self.k
        if self.dis_l1 > -self.disy2:
            self.dis_l1 = -self.disy2

        if self.dis_l2 != -1e10:
            self.k = self.fly/(self.dis_l2-x_)
            self.b = -self.k*x_
            self.state = 13
            return  # 9->13

        self.k = (self.a2*self.k0*self.dis_l1-self.fy2+self.a2*self.k0*self.disy2)/(self.dis_l1-x_)
        self.b = -self.k*x_
        self.state = 11
        return  # 9->11

    def takeda_10(self):

        if self.dis < self.dis_l2:
            y_ = self.k*self.dis_l2+self.b
            self.k = (self.a2*self.k0*self.dis_l1-self.fy2+self.a2*self.k0*self.disy2-y_)/(self.dis_l1-self.dis_l2)
            self.b = y_-self.k*self.dis_l2
            self.dis_l2 = -1e10
            self.state = 11
            return  # 10->11

        y_ = self.k*self.dis+self.b
        if y_ < self.a2*self.k0*self.dis-self.fy2+self.a2*self.k0*self.disy2:
            self.k = self.a2*self.k0
            self.b = -self.fy2+self.a2*self.k0*self.disy2
            self.state = 8
            return  # 10->8

        if y_ < 0:
            return  # 10->10

        x_ = -self.b/self.k
        if self.dis_r1 < self.disy2:
            self.dis_r1 = self.disy2

        if self.dis_r2 != 1e10:
            self.k = self.fry/(self.dis_r2-x_)
            self.b = -self.k*x_
            self.state = 14
            return  # 10->14

        self.k = (self.a2*self.k0*self.dis_r1+self.fy2-self.a2*self.k0*self.disy2)/(self.dis_r1-x_)
        self.b = -self.k*x_
        self.state = 12
        return  # 10->12

    def takeda_11(self):

        if self.dis < self.dis_l1:
            self.k = self.a2*self.k0
            self.b = -self.fy2+self.a2*self.k0*self.disy2
            self.state = 8
            return  # 11->8

        if self.dis > self.dis0:
            self.dis_l2 = self.dis0
            self.fly = self.k*self.dis_l2+self.b
            self.k = self.kl
            self.b = self.fly-self.k*self.dis_l2
            self.state = 10
            return  # 11->10

        return

    def takeda_12(self):
        if self.dis > self.dis_r1:
            self.k = self.a2*self.k0
            self.b = self.fy2-self.a2*self.k0*self.disy2
            self.state = 7  # 12->7
            return

        if self.dis < self.dis0:
            self.dis_r2 = self.dis0
            self.fry = self.k*self.dis_r2+self.b
            self.k = self.kr
            self.b = self.fry-self.k*self.dis_r2
            self.state = 9  # 12->9
            return

        return

    def takeda_13(self):

        if self.dis < self.dis_l2:
            self.dis_r2 = 1e10
            self.k = (self.a2*self.k0*self.dis_l1-self.fy2+self.a2*self.k0*self.disy2-self.fly)/(self.dis_l1-self.dis_l2)
            self.b = self.fly-self.k*self.dis_l2
            self.state = 11  # 13->11
            return

        if self.dis > self.dis0:
            self.dis_l3 = self.dis0
            y_ = self.k*self.dis_l3+self.b
            self.k = self.kl
            self.b = y_-self.k*self.dis_l3
            self.state = 15  # 13->15
            return

        return

    def takeda_14(self):
        if self.dis > self.dis_r2:
            self.dis_l2 = -1e10
            self.k = (self.a2*self.k0*self.dis_r1+self.fy2-self.a2*self.k0*self.disy2-self.fry)/(self.dis_r1-self.dis_r2)
            self.b = self.fry-self.k*self.dis_r2
            self.state = 12  # 14->12
            return

        if self.dis < self.dis0:
            self.dis_r3 = self.dis0
            y_ = self.k*self.dis_r3+self.b
            self.k = self.kr
            self.b = y_-self.k*self.dis_r3
            self.state = 16  # 14->16
            return

        return

    def takeda_15(self):

        y_ = self.k*self.dis+self.b
        if y_ > 0:
            x_ = -self.b/self.k
            self.k = self.fry/(self.dis_r2-x_)
            self.b = -self.k*x_
            self.state = 14							# 15->14
            return

        if self.dis < self.dis_l3:
            y_ = self.k*self.dis_l3+self.b
            self.k = (self.fly-y_)/(self.dis_l2-self.dis_l3)
            self.b = y_-self.k*self.dis_l3
            self.state = 13
            return 							# 15->13

        return

    def takeda_16(self):

        y_ = self.k*self.dis+self.b
        if y_ < 0:
            x_ = -self.b/self.k
            self.k = self.fly/(self.dis_l2-x_)
            self.b = -self.k*x_
            self.state = 13							# 16->13
            return

        if self.dis > self.dis_r3:
            y_ = self.k*self.dis_r3+self.b
            self.k = (self.fry-y_)/(self.dis_r2-self.dis_r3)
            self.b = y_-self.k*self.dis_r3
            self.state = 14
            return 							# 16->14

        return

    def takeda_17(self):

        if self.dis > self.dis_r1:
            self.k = self.a2*self.k0
            self.b = self.fy2-self.a2*self.k0*self.disy2
            self.state = 7
            return 							# 17->7

        y_ = self.k*self.dis+self.b
        if y_ < -self.fy1:
            x_ = (-self.fy1-self.b)/self.k
            self.k = (-self.fy2+self.fy1)/(-self.disy2-x_)
            self.b = -self.fy1-self.k*x_
            self.state = 19
            return 							# 17->19

        return

    def takeda_18(self):

        if self.dis < self.dis_l1:
            self.k = self.a2*self.k0
            self.b = -self.fy2+self.a2*self.k0*self.disy2
            self.state = 8
            return 							# 18->8

        y_ = self.k*self.dis+self.b
        if y_ > self.fy1:
            x_ = (self.fy1-self.b)/self.k
            self.k = (self.fy2-self.fy1)/(self.disy2-x_)
            self.b = self.fy1-self.k*x_
            self.state = 20
            return 							# 18->20

        return

    def takeda_19(self):

        if self.dis < -self.disy2:
            self.k = self.a2*self.k0
            self.b = -self.fy2+self.a2*self.k0*self.disy2
            self.state = 8
            return 							# 19->8

        if self.dis > self.dis0:
            self.dis_l2 = self.dis0
            self.fly = self.k*self.dis0+self.b
            self.k = self.kp
            self.b = self.fly-self.k*self.dis_l2
            self.state = 21
            return 							# 19->21

        return

    def takeda_20(self):

        if self.dis > self.disy2:
            self.k = self.a2*self.k0
            self.b = self.fy2-self.a2*self.k0*self.disy2
            self.state = 7
            return 							# 20->7

        if self.dis < self.dis0:
            self.dis_r2 = self.dis0
            self.fry = self.k*self.dis0+self.b
            self.k = self.kp
            self.b = self.fry-self.k*self.dis_r2
            self.state = 22
            return 							# 20->22

        return

    def takeda_21(self):
        if self.dis < self.dis_l2:
            self.k = (-self.fy2-self.fly)/(-self.disy2-self.dis_l2)
            self.b = self.fly-self.k*self.dis_l2
            self.state = 19
            return 							# 21->19

        y_ = self.k*self.dis+self.b
        if y_ > 0:
            x_ = -self.b/self.k
            self.k = (self.a2*self.k0*self.dis_r1+self.fy2-self.a2*self.k0*self.disy2)/(self.dis_r1-x_)
            self.b = -self.k*x_
            self.state = 23
            return 							# 21->23

        return

    def takeda_22(self):

        if self.dis > self.dis_r2:
            self.k = (self.fy2-self.fry)/(self.disy2-self.dis_r2)
            self.b = self.fry-self.k*self.dis_r2
            self.state = 20
            return 							# 22->20

        y_ = self.k*self.dis+self.b
        if y_ < 0:
            x_ = -self.b/self.k
            self.k = (self.a2*self.k0*self.dis_l1-self.fy2+self.a2*self.k0*self.disy2)/(self.dis_l1-x_)
            self.b = -self.k*x_
            self.state = 24
            return 							# 22->24

        return

    def takeda_23(self):

        if self.dis > self.dis_r1:
            self.k = self.a2*self.k0
            self.b = self.fy2-self.a2*self.k0*self.disy2
            self.state = 7
            return 							# 23->7

        if self.dis < self.dis0:
            self.dis_r3 = self.dis0
            y_ = self.k*self.dis_r3+self.b
            self.k = self.kr
            self.b = y_-self.k*self.dis_r3
            self.state = 25
            return 							# 23->25

        return

    def takeda_24(self):

        if self.dis < self.dis_l1:
            self.k = self.a2*self.k0
            self.b = -self.fy2+self.a2*self.k0*self.disy2
            self.state = 8
            return 							# 24->8

        if self.dis > self.dis0:
            self.dis_l3 = self.dis0
            y_ = self.k*self.dis_l3+self.b
            self.k = self.kl
            self.b = y_-self.k*self.dis_l3
            self.state = 26
            return 							# 24->26

        return

    def takeda_25(self):

        if self.dis > self.dis_r3:
            y_ = self.k*self.dis_r3+self.b
            self.k = (self.a2*self.k0*self.dis_r1+self.fy2-self.a2*self.k0*self.disy2-y_)/(self.dis_r1-self.dis_r3)
            self.b = y_-self.k*self.dis_r3
            self.state = 23
            return 							# 25->23

        y_ = self.k*self.dis+self.b
        if y_ < 0:
            x_ = -self.b/self.k
            self.k = self.fly/(self.dis_l2-x_)
            self.b = -self.k*x_
            self.state = 27
            return 							# 25->27

        return

    def takeda_26(self):

        if self.dis < self.dis_l3:
            y_ = self.k*self.dis_l3+self.b
            self.k = (self.a2*self.k0*self.dis_l1-self.fy2+self.a2*self.k0*self.disy2-y_)/(self.dis_l1-self.dis_l3)
            self.b = y_-self.k*self.dis_l3
            self.state = 24
            return 							# 26->24

        y_ = self.k*self.dis+self.b
        if y_ > 0:
            x_ = -self.b/self.k
            self.k = self.fry/(self.dis_r2-x_)
            self.b = -self.k*x_
            self.state = 28
            return 							# 26->28

        return

    def takeda_27(self):

        if self.dis < self.dis_l2:
            self.k = (-self.fy2-self.fly)/(-self.disy2-self.dis_l2)
            self.b = self.fly-self.k*self.dis_l2
            self.state = 19
            return 							# 27->19

        if self.dis > self.dis0:
            self.dis_l3 = self.dis0
            y_ = self.k*self.dis_l3+self.b
            self.k = self.kp
            self.b = y_-self.k*self.dis_l3
            self.state = 29
            return 							# 27->29

        return

    def takeda_28(self):

        if self.dis > self.dis_r2:
            self.k = (self.fy2-self.fry)/(self.disy2-self.dis_r2)
            self.b = self.fry-self.k*self.dis_r2
            self.state = 20
            return 							# 28->20

        if self.dis < self.dis0:
            self.dis_r3 = self.dis0
            y_ = self.k*self.dis_r3+self.b
            self.k = self.kp
            self.b = y_-self.k*self.dis_r3
            self.state = 30
            return 							# 28->30

        return

    def takeda_29(self):

        if self.dis < self.dis_l3:
            y_ = self.k*self.dis_l3+self.b
            self.k = (self.fly-y_)/(self.dis_l2-self.dis_l3)
            self.b = self.fly-self.k*self.dis_l2
            self.state = 27
            return 							# 29->27

        y_ = self.k*self.dis+self.b
        if y_ > 0:
            x_ = -self.b/self.k
            self.k = (self.a2*self.k0*self.dis_r1+self.fy2-self.a2*self.k0*self.disy2)/(self.dis_r1-x_)
            self.b = -self.k*x_
            self.state = 23
            return 							# 29->23

        return

    def takeda_30(self):

        if self.dis > self.dis_r3:
            y_ = self.k*self.dis_r3+self.b
            self.k = (self.fry-y_)/(self.dis_r2-self.dis_r3)
            self.b = self.fry-self.k*self.dis_r2
            self.state = 28
            return 							# 30->28

        y_ = self.k*self.dis+self.b
        if y_ < 0:
            x_ = -self.b/self.k
            self.k = (self.a2*self.k0*self.dis_l1-self.fy2+self.a2*self.k0*self.disy2)/(self.dis_l1-x_)
            self.b = -self.k*x_
            self.state = 24
            return 							# 30->24

        return
