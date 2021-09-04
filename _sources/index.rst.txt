.. cvts documentation master file, created by
   sphinx-quickstart on Sat Jun  5 12:10:15 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CVTS's Developer Documentation
==============================

.. toctree::
   :maxdepth: 2

   cvts
   etl
   config
   input
   output
   scripts



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`



Glossary
========

This glossary is tuned to how we use the terms within CVTS, which is often
different on how they are used more generally.

.. glossary::

    geometry
        A spatial object (at present, a Polygon or MultiPolygon) that designates
        some area of interest.

    geography
        A set of :term:`geometries<geometry>` that specify regionalisations of
        interest. see :ref:`here<geographies-data>` for a description of what is
        required in this package.

    stop point
        A location where a vehicle has not moved for more than
        :py:data:`cvts.settings.MIN_STOP_TIME` seconds.

    trip
        A journey between two :term:`stop points<stop point>`.

    way id
        Identifiers for road segments (as defined in Open Stree Map).
