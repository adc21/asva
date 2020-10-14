"""データの読み込み"""
import numpy as np

def fs_from_fi(fi: list):
    fliped = np.flipud(fi)
    fs = np.array([])

    for i, f in enumerate(fliped):
        f2 = fs[0] if len(fs) > 0 else 0
        fs = np.insert(fs, 0, f + f2)

    fs = np.reshape(fs, (len(fs), 1))
    
    return fs
