"""Stopper の抵抗力
"""
from typing import TypedDict
from asva.dampers.Damper import Damper

class StopperType(TypedDict):
    k: float
    ft: float

class Stopper(Damper):
    def __init__(self, dt: float, Nd: float, k: float, ft: float):
        super().__init__(dt, Nd)
        self.off = False
        self.k = k
        self.ft = ft
        self.force: float = 0

    def step(self, dis: float):
        # init
        self.init_step(dis)

        if self.off:
            self.force = 0
        else:
            self.force = self.k * self.dis * self.Nd
            if abs(self.force) > self.ft * self.Nd:
                self.off = True

        # end
        self.end_step()
        return self.force
