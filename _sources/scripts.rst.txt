*******
Scripts
*******

Python scripts used in CVTS. These are installed with the python package.




Utilities for Individual Files
==============================

csv2json
--------

Python script for converting CSVs to JSON appropriate for feeding to the
`trace_attributes`_ service of Valhalla. This is convenient for converting
single files when testing/playing/etc.

json2geojson
------------

Python script for converting the json files produced by the `trace_attributes`_
service of Valhalla to GeoJSON files. This is also useful for
testing/playing/ect.

createdb
--------

TODO

loadvehicles
------------

TODO




Entry Points for the (`Luigi`_) Workflow
========================================

These scripts ensure that various `tasks`_ are complete.

The results of these scripts are saved in sub-folders of the

processtraces
-------------

Script for matching all raw data to the road network.

processall
----------

Script for extracting:

- stops by region,
- stops on a (0.1 degree) raster,
- source and destination counts,
- speeds by :term:`way ids<way id>`. These are calculated by road segment by
  time of day for each vehicle. These are first produced on disk, then saved in
  an SQL database (see :py:class:`cvts.models.Traversal` for an ORM
  representation of the the rows).

Because of the dependencies, this would also trigger the (`Luigi`_) tasks that
would be run by `processtraces`_ if required.



Misc
====

createpgdb
----------

Script to generate the database defined by the (ORM) classes in
:py:mod:`cvts.models`.

**BE CAREFUL WITH THIS... it will first drop tables and alike created previously
and hence you can lose your data**.



.. _trace_attributes: https://valhalla.readthedocs.io/en/latest/api/map-matching/api-reference/#outputs-of-trace_attributes

.. _Luigi: https://github.com/spotify/luigi

.. _tasks: https://luigi.readthedocs.io/en/stable/tasks.html
