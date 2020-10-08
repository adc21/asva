import copy

class RestoringForce:
    def __init__(self):
        self.force: float = 0
        self.dis: float = 0
        self.dis0: float = 0
        self.d_dis: float = 0
        self.d_dis0: float = 0

    def init_step(self, dis: float) -> None:
        self.dis = dis
        self.d_dis = dis - self.dis0

    def end_step(self, k: float):
        self.dis0 = copy.copy(self.dis)
        self.d_dis0 = copy.copy(self.d_dis)
        self.force = self.force + k * self.d_dis
