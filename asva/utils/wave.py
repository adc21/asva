"""データの読み込み"""
from typing import TextIO, Optional
import numpy as np

from asva.Types import WaveType, CASESType

#import pandas as pd

def read_wave(file_path: TextIO, col: int, delimiter: Optional[str], skiprows: int):
    try:
        #df = pd.read_csv(opened_file, header=None, skiprows=skiprows, usecols=[col], delimiter=delimiter)*amp*to_meter
        #wave = df[col]
        wave = np.loadtxt(file_path, usecols=[col], delimiter=delimiter, skiprows=skiprows)
    except Exception as error:
        raise ValueError(f"check wave setting: {error}")

    return wave

def read_case_wave(wave: WaveType, case_conf: CASESType):
    """ケースとその地震設定に基づき、地震ファイルを読み込んでarrayを返す"""
    open_file = wave['INPUT_FILE']
    encording_setting = 'ENCORDING' in wave
    encording = wave['ENCORDING'] if encording_setting else 'shift-jis'

    try:
        opened_file = open(open_file, 'r', encoding=encording)
    except OSError:
        raise ValueError(f"cannot open {open_file}")

    col = wave['COL']
    delimiter = wave['DELIMITER']
    skiprows = wave['SKIPROWS']
    to_meter = wave['TO_METER']
    amp = case_conf['AMP']

    wave = read_wave(opened_file, col, delimiter, skiprows)*amp*to_meter

    return wave

def add_wave_required_zero(wave: list, required_length: int):
    n_wave = len(wave)
    length = max(n_wave, required_length)
    new_wave = np.zeros(length)

    for n in range(n_wave):
        new_wave[n] = wave[n]

    return new_wave

def divide_wave(wave: list, n_div: int):
    n_wave = len(wave) * n_div

    acc_00 = np.zeros(n_wave)
    acc_g = 0
    for n in range(n_wave):
        wave_step = n // n_div
        wave_step0 = wave_step - 1
        acc_g1 = wave[wave_step0] if wave_step >= 1 else 0
        acc_g2 = wave[wave_step]
        dacc_g = (acc_g2 - acc_g1) / n_div
        acc_g = acc_g + dacc_g
        acc_00[n] = acc_g

    return acc_00