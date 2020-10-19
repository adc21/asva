=======
Dampers
=======

Dampers can be defined and set to ``AnalysisConfig`` like below.

You can register several dampers in config and choose it in ``CASES``.


.. code::

    # Example
    import asva as ap

    Oil: ap.VDBType = {
        'c1': 100,
        'c2': 50,
        'vr': 0.75,
        'vel_max': 1.5,
    }

    config: ap.AnalysisConfigType = {
        ...,
        'CASES': [
            {
                'DAMPER': 'VDB_DAMPERS',
                ...,
            },
        ],
        ...,
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
        ...,
    }


MASS Damper
===========

``type`` MASS

.. code::

    class MASSType(TypedDict):
        m: float

Stopper
=======

``type`` Stopper

.. code::

    class StopperType(TypedDict):
        k: float
        ft: float

Viscous Damper (CV^α)
=====================

``type`` VDA

.. code::

    class VDAType(TypedDict):
        cd: float
        alpha: float
        vy: Optional[float]
        vel_max: Optional[float]

Viscous Damper (Bilinear)
=========================

``type`` VDB

.. code::

    class VDBType(TypedDict):
        c1: float
        c2: float
        vr: float
        vel_max: float

TMD
===

``type`` TMD

.. code::

    class TMDType(TypedDict):
        md: float
        cd: float
        kd: float

iRDT
====

``type`` iRDT

.. code::

    class iRDTType(TypedDict):
        md: float
        cd: float
        alpha: float
        kb: float
        fr: float
        cosA: float

.. toctree::
   :maxdepth: 1
   :hidden:


