from asva.src.restoring_force.RestoringForce import RestoringForce

class Gyakko(RestoringForce):
    def __init__(self, k0, a1, a2, f1, f2):
        super().__init__()
        self.k0 = k0
        self.k = self.k0
        self.a1 = a1
        self.a2 = a2
        self.f1 = f1
        self.f2 = f2
        self.disc = self.f1 / self.k0
        self.disy = (self.f2 - (1 - self.a1) * self.f1) / (self.a1 * self.k0)

    def step(self, dis) -> float:
        # init
        self.init_step(dis)

        if abs(dis) < self.disc:
            self.k = self.k0
        elif abs(dis) < self.disy:
            self.k = self.a1 * self.k0
        else:
            self.k = self.a2 * self.k0

        # end
        self.end_step(self.k)
        return self.k