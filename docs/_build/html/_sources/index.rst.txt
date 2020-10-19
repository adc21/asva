.. asva documentation master file, created by
   sphinx-quickstart on Fri Oct 16 09:53:05 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. important::

    It is **very important** to check accuracy of asva analysis on your own for production use since asva is under development. Please report bugs to `Github Issues <https://github.com/adc21/asva/issues>`_.

====
asva
====


asva is a package to simulate vibration response of multi degree of freedom system subjected to earthquakes.
Response time history and amplitude can be calculated.


Quick Start
===========

Requirements
------------

Python 3.8+

Installation
------------

.. code::

   pip install asva


Minimum code example
--------------------

.. code::

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
      'N_DOF': 1,
      'BASE_ISOLATION': False,
      'H': 0.02,
      'H_TYPE': 0,
      'I': [
         [1],
      ],
      'HEIGHT': [4],
      'MI': [100],
      'KI': [
         [{
               'type': 'elastic',
               'k0': 4000,
         }, ],
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



.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: Contents:

   src/setup_config
   src/hysteretic_models
   src/dampers

General Indices
===============

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
