import asva as ap
from examples.configs import config, amp_config, export_config

def main():
    analysis = ap.Analysis(config, 0, amp_config, export_config)   # ０は最初のケースを回す。
    analysis.analysis()
    analysis.amplitude()
    analysis.exporter.print()
    analysis.exporter.export()
    analysis.plot.all()

if __name__ == '__main__':
    main()
