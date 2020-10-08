import numpy as np

def damper_param_along_storeys(n_dof: int, damper_type: str, damper_target_param: str, dampers: list, add_all_param: bool =False) -> np.ndarray:
    """
    同じタイプのダンパーの特定のパラメータを探して配列にまとめる
    add_all_param: Trueの場合同じ層の値を全て足し合わせる（ダンパー内の自由度が一つである場合のみ）、Falseの場合最初の一つ目のみ
    """
    DAMPER_MATRIX = np.array([])

    for n in range(n_dof):
        value = 10**(-10)
        num_dampers = len(dampers[n])

        for nn in range(num_dampers):
            if dampers[n][nn]["type"] == damper_type:
                damper = dampers[n][nn]["d"]
                nd = dampers[n][nn]["Nd"]
                value = value + damper[damper_target_param] * nd

                if not add_all_param:
                    break

        DAMPER_MATRIX = np.append(DAMPER_MATRIX, value)

    return DAMPER_MATRIX

def add_zeros_to_damper_matrix(DM: np.ndarray, size: int):
    DM_size = np.size(DM,0)
    add_size = size - DM_size

    DM = np.concatenate((np.concatenate((DM, np.zeros((add_size, DM_size)))), np.concatenate((np.zeros((DM_size, add_size)), np.zeros((add_size, add_size))))), axis=1)

    return DM

def damper_exists(n_dof: int, damper_type: str, dampers: list) -> bool:
    for n in range(n_dof):
        num_dampers = len(dampers[n])

        for nn in range(num_dampers):
            if dampers[n][nn]["type"] == damper_type:
                return True

    return False
