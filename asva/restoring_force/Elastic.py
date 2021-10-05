from asva.restoring_force.RestoringForce import RestoringForce

class Elastic(RestoringForce):
    def step(self, dis: float) -> None:
        # init
        self.init_step(dis)
        # end
        self.end_step(self.k0)
