from asva.src.restoring_force.RestoringForce import RestoringForce

class Elastic(RestoringForce):
    def __init__(self, k0):
        super().__init__()
        self.k0 = k0

    def step(self, dis: float) -> float:
        # init
        self.init_step(dis)
        # end
        self.end_step(self.k0)
        return self.k0