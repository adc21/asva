from typing import List, Optional, Union
from asva.dampers.iRDT import *
from asva.dampers.TMD import *
from asva.dampers.MASS import *
from asva.dampers.VDA import *
from asva.dampers.VDB import *
from asva.dampers.Stopper import *

DamperClassType = Union[VDA, iRDT, TMD, MASS, VDB, Stopper]

def create_damper_instances(analysis):
    d: List[List[DamperClassType]] = []
    dt = analysis.ddt
    for i in range(analysis.model.n_dof):
        row: List[DamperClassType] = []
        for ii in range(analysis.max_nd):
            try:
                df = analysis.dampers[i][ii]
            except IndexError:
                continue

            # 弾性
            if df["type"] == "iRDT":
                Nd = df["Nd"]
                md = df["d"]["md"]
                cd = df["d"]["cd"]
                alpha = df["d"]["alpha"]
                kb = df["d"]["kb"]
                fr = df["d"]["fr"]
                cosA = df["d"]["cosA"]
                row.append(iRDT(dt, Nd, md, cd, alpha, kb, fr, cosA))
            elif df["type"] == "TMD":
                Nd = df["Nd"]
                md = df["d"]["md"]
                cd = df["d"]["cd"]
                kd = df["d"]["kd"]
                row.append(TMD(dt, Nd, md, cd, kd))
            elif df["type"] == "MASS":
                Nd = df["Nd"]
                m = df["d"]["m"]
                row.append(MASS(dt, Nd, m))
            elif df["type"] == "VDA":
                Nd = df["Nd"]
                cd = df["d"]["cd"]
                alpha = df["d"]["alpha"]

                try:
                    vy = df["d"]["vy"]
                except KeyError:
                    vy = None

                try:
                    vel_max = df["d"]["vel_max"]
                except KeyError:
                    vel_max = None

                row.append(VDA(dt, Nd, cd, alpha, vy, vel_max))
            elif df["type"] == "VDB":
                Nd = df["Nd"]
                c1 = df["d"]["c1"]
                c2 = df["d"]["c2"]
                vr = df["d"]["vr"]
                vel_max = df["d"]["vel_max"]
                row.append(VDB(dt, Nd, c1, c2, vr, vel_max))
            elif df["type"] == "Stopper":
                Nd = df["Nd"]
                k = df["d"]["k"]
                ft = df["d"]["ft"]
                row.append(Stopper(dt, Nd, k, ft))
            else:
                raise ValueError(f"No match type specified for damper type {df['type']}")

        d.append(row)

    return d
