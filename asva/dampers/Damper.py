"""基本のダンパークラス"""
import copy


class Damper():
    def __init__(self, dt: float, Nd: float):
        self.j = 2
        self.dt = dt
        self.Nd = Nd
        self.dis: float = 0
        self.dis0: float = 0
        self.vel: float = 0
        self.vel0: float = 0
        self.acc: float = 0
        self.acc0: float = 0

    def init_step(self, dis: float):
        d_dis = dis - self.dis0
        d_vel = self.j / self.dt * d_dis - self.j * self.vel0
        d_acc = (self.j / self.dt)**2 * d_dis - self.j * ((self.j / self.dt) * self.vel0 + self.acc0)

        self.dis = dis
        self.vel += d_vel
        self.acc += d_acc

    def end_step(self):
        self.dis0 = copy.copy(self.dis)
        self.vel0 = copy.copy(self.vel)
        self.acc0 = copy.copy(self.acc)
