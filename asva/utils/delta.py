"""データの読み込み"""
import numpy as np

def delta(vector: list):
    return np.insert(np.diff(vector), 0, vector[0]) if len(vector) > 0 else vector
