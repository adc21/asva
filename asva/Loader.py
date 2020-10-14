import pandas as pd

class Loader:

    def __init__(self, analysis):
        self.analysis = analysis
        self.max_df = pd.DataFrame()
        self.amp_df = pd.DataFrame()
        self.th_df = pd.DataFrame()

    def read_csv(self, file_path):
        try:
            data = pd.read_csv(file_path)
        except:
            data = pd.DataFrame()

        return data

    def load_th(self):
        self.max_df = self.read_csv(self.analysis.exporter.result_data_dir + 'max.csv')
        self.th_df = self.read_csv(self.analysis.exporter.result_data_dir + 'time_history.csv')

    def load_amp(self):
        self.amp_df = self.read_csv(self.analysis.exporter.result_data_dir + 'amp.csv')
