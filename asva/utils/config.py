import os
import re

from asva.Types import AnalysisConfigType, AsvaAnalysisConfigType, AmplitudeConfigType, AsvaAmplitudeConfigType, ExportConfigType, AsvaExportConfigType

additional_analysis_config = {
    'TEST': False,                # asva.test.settingsで実行
    'MAX_ND': [],
}

additional_amplitude_config = {
    'MAX_NK': 0,
}

additional_export_config = {
    'RESULT_DATA_CASES_DIR': [],
    'RESULT_DATA_DIR': [],
    'RESULT_PLOT_DIR': [],
}

def init_analysis_config(user_config: AnalysisConfigType) -> AsvaAnalysisConfigType:
    config: AsvaAnalysisConfigType = {**user_config, **additional_analysis_config}   # type: ignore
    N_DOF = len(config['MI'])

    # Validate Setting Model
    for i, case in enumerate(config['CASES']):
        dampers = config['DAMPERS'][config['CASES'][i]["DAMPER"]]
        if not (N_DOF <= len(config['KI']) and N_DOF == len(dampers)):
            raise ValueError(f"警告：config.model.DAMPER{i}番目mf,kf,dampersの配列長さはNと同じである必要があります。")

    MAX_ND = 0
    for i, case in enumerate(config['CASES']):
        dampers = config['DAMPERS'][config['CASES'][i]["DAMPER"]]
        for n in range(N_DOF):
            MAX_ND = len(dampers[n]) if len(dampers[n]) > MAX_ND else MAX_ND
        config['MAX_ND'].append(MAX_ND)  # 1層あたりのダンパー種類最大数

    config['G'] = 9.80665

    return config

def init_amplitude_config(user_config: AmplitudeConfigType) -> AsvaAmplitudeConfigType:
    config: AsvaAmplitudeConfigType = {**user_config, **additional_amplitude_config}   # type: ignore

    return config


def init_export_config(analysis_config: AsvaAnalysisConfigType, user_export_config: ExportConfigType) -> AsvaExportConfigType:
    config: AsvaExportConfigType = {**user_export_config, **additional_export_config}   # type: ignore

    # Result Data
    RESULT_DIR = config['RESULT_DIR'] if re.match(
        r'/$', config['RESULT_DIR']) else config['RESULT_DIR'] + '/'
    config['RESULT_DIR'] = RESULT_DIR
    if not os.path.isdir(RESULT_DIR):
        os.mkdir(RESULT_DIR)

    for i, case in enumerate(analysis_config['CASES']):
        result_case_dir = RESULT_DIR + '/' + case['NAME']
        config['RESULT_DATA_CASES_DIR'].append(result_case_dir)
        config['RESULT_DATA_DIR'].append(
            result_case_dir + '/' + config['RESULT_DATA_DIR_NAME'] + '/')
        config['RESULT_PLOT_DIR'].append(
            result_case_dir + '/' + config['RESULT_PLOT_DIR_NAME'] + '/')

        if not os.path.isdir(config['RESULT_DATA_CASES_DIR'][i]):
            os.mkdir(config['RESULT_DATA_CASES_DIR'][i])
        if not os.path.isdir(config['RESULT_DATA_DIR'][i]):
            os.mkdir(config['RESULT_DATA_DIR'][i])
        if not os.path.isdir(config['RESULT_PLOT_DIR'][i]):
            os.mkdir(config['RESULT_PLOT_DIR'][i])

    return config
