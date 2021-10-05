import asva as ap

config: ap.AnalysisConfigType = {
    # analysis
    'BETA': 1 / 4,

    # case
    'CASES': [
        {
            'NAME': 'Example',
            'WAVE': 'Sample',
            'AMP': 1,
            'DAMPER': 'None',
            'NDIV': 2,
            'START_TIME': 0,
            'END_TIME': None,
        },
    ],

    # damper
    'DAMPERS': {
        'None': [
            [],
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


def main():
    analysis = ap.Analysis(config, 0)   # ０は最初のケースを回す。
    analysis.analysis()
    print(analysis.resp.dis)

if __name__ == '__main__':
    main()
