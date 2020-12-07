import copy

class RestoringForce:
    def __init__(self, n1: int, n2: int, k0: float):
        if n1 == n2:
            raise ValueError('n1 and n2 must not be same number.')

        if n1 < n2:
            self.n1 = n1
            self.n2 = n2
        else:
            self.n1 = n2
            self.n2 = n1

        self.k0 = k0
        self.k = self.k0
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
