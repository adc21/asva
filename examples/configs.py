import asva as ap

Oil: ap.VDBType = {
    'c1': 100,
    'c2': 50,
    'vr': 0.75,
    'vel_max': 1.5,
}

config: ap.AnalysisConfigType = {
    # analysis
    'BETA': 1 / 4,

    # case
    'CASES': [
        {
            'NAME': 'Example',
            'WAVE': 'Sample',
            'AMP': 1,
            'DAMPER': 'VDB_DAMPERS',
            'NDIV': 5,
            'START_TIME': 0,
            'END_TIME': None,
        },
    ],

    # damper
    'DAMPERS': {
        'VDB_DAMPERS': [
            [
                {
                    'type': 'VDB',
                    'Nd': 1,
                    'd': Oil,
                },
            ],
        ],
    },

    # model
    'BASE_ISOLATION': False,
    'H': 0.02,
    'H_TYPE': 0,
    'I': [
        [1],
    ],
    'MI': [100],
    'KI': [
        {
            'n1': 0,
            'n2': 1,
            'type': 'elastic',
            'k0': 4000,
        },
    ],

    # wave
    'WAVES': {
        'Sample': {
            'NAME': 'Sample',
            'DT': 0.02,
            'NDATA': 2688,
            'TO_METER': 0.01,
            'INPUT_FILE': 'wave/Sample.csv',
            'DELIMITER': None,
            'SKIPROWS': 3,
            'COL': 0,
            'ENCORDING': 'utf',
        },
    },
}

amp_config: ap.AmplitudeConfigType = {
    'N_W': 5000,
    'DF': 0.001,
}

export_config: ap.ExportConfigType = {
    'RESULT_DIR': 'work',
    'RESULT_DATA_DIR_NAME': 'data',
    'RESULT_PLOT_DIR_NAME': 'plot',
    'DATA_PLOT_STORIES': None,
}
