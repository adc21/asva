"""基本のダンパークラス"""
import copy


class Damper():
    def __init__(self, dt: float, Nd: float):
        self.dt = dt
        self.Nd = Nd
        self.dis: float = 0
        self.dis0: float = 0
        self.vel: float = 0
        self.vel0: float = 0
        self.acc: float = 0
        self.acc0: float = 0

    def init_step(self, dis: float):
        self.dis = dis
        self.vel = 2 * (self.dis - self.dis0) / self.dt - self.vel0
        self.acc = 2 * (self.vel - self.vel0) / self.dt - self.acc0

    def end_step(self):
        self.dis0 = copy.copy(self.dis)
        self.vel0 = copy.copy(self.vel)
        self.acc0 = copy.copy(self.acc)
