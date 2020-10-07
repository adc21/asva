"""データの読み込み"""
from asva.src.Types import WaveType, CASESType

def time_step(wave: WaveType, case_conf: CASESType):
    n_div = case_conf['NDIV']
    dt = wave['DT']
    ddt = dt / n_div
    start_time: float = case_conf['START_TIME'] if case_conf['START_TIME'] else 0   # type: ignore
    end_time: float = case_conf['END_TIME'] if case_conf['END_TIME'] else dt * wave['NDATA'] # type: ignore
    res_start_step = int(start_time / dt)
    res_end_step = int(end_time / dt)
    res_n_steps = res_end_step - res_start_step
    start_step = res_start_step * n_div
    end_step = res_end_step * n_div
    n_steps = end_step - start_step
    return n_div, dt, ddt, start_time, end_time, res_start_step, res_end_step, res_n_steps, start_step, end_step, n_steps
