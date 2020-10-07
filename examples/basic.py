import asva as ap

Oil: ap.VDBType = {
    "c1": 100,
    "c2": 50,
    "vr": 0.75,
    "vel_max": 1.5,
}

config: ap.ConfigType = {
    # analysis
    'BETA': 1 / 4,
    'BASE_ISOLATION': False,
    'N_W': 5000,
    'DF': 0.001,

    # case
    'CASES': [
        {
            'NAME': 'Example',
            'WAVE': 'Sample',
            'AMP': 1,
            'DAMPER': 'VDB_DAMPERS',
            'NDIV': 10,
            'START_TIME': 0,
            'END_TIME': None,
        },
    ],

    # damper
    'DAMPERS': {
        "VDB_DAMPERS": [
            [
                {
                    "type": "VDB",
                    "Nd": 1,
                    "d": Oil,
                },
            ],
        ],
    },

    # model
    'N_DOF': 1,
    'H': 0.02,
    'H_TYPE': 0,
    'I': [
        [1],
    ],
    'HEIGHT': [4],
    'MI': [100],
    'KI': [
        [{
            "type": "elastic",
            "k0": 4000,
        }, ],
    ],

    # result
    'RESULT_DIR': 'work',
    'RESULT_DATA_DIR_NAME': 'data',
    'RESULT_PLOT_DIR_NAME': 'plot',
    'DATA_PLOT_STORIES': None,

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


def main():
    analysis = ap.Analysis(config, 0)   # ０は最初のケースを回す。
    analysis.analysis()
    analysis.amplification()
    analysis.print()
    analysis.export()
    analysis.plot()


if __name__ == '__main__':
    main()
