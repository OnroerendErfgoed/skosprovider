.. _development:

Development
===========

While skosprovider is still in development, the basic premise is fairly
stable and the API changes have been fairly minor from version to version. We do
continue to refine the project and make the providers more expressive.

We try to cover as much code as we can with unit tests. You can run them with
pytest_. When providing a pull request, please run the unit tests first and
make sure they all pass. Please provide new unit tests to maintain 100%
coverage.

.. code-block:: bash

    # Setup for development
    $ pip install -r requirements-dev.txt
    $ pip install -e .
    # No coverage
    $ pytest
    # Coverage
    $ pytest --cov skosprovider --cov-report term-missing
    # Only run a subset of the tests
    $ pytest tests/test_registry.py
    $ pytest tests/rdf

.. _pytest: https://pytest.org

Extra data loaders and dumpers
------------------------------

In the skos model, the ``extra_data`` of an object is always an
:class:`rdflib.Graph` or `None`. Every format skosprovider reads and writes has
its own package, eg. :mod:`skosprovider.jsonld`, and its own loaders and
dumpers in the ``extra_data`` module of that package. They all follow the same
rule:

* A **loader** receives the input of a single object in the format of its
  package, and the skos object built from it, and returns a
  :class:`rdflib.Graph` or `None`. The skos object is fully built except for
  its ``extra_data``, so the loader can tell what kind of object it loads.
* A **dumper** receives a skos object, and so its ``extra_data`` graph, and
  returns the extra data in the format of its package, or `None`.

====================================  ===============================  ========================
Package                               Loader input                     Dumper output
====================================  ===============================  ========================
:mod:`skosprovider.dictionary`        the dict of the object           a dict
:mod:`skosprovider.csv`               the csv row (a list of strings)  the text of a csv cell
:mod:`skosprovider.rdf`               the graph of the object          a graph
:mod:`skosprovider.jsonld`            the JSON-LD node of the object   a JSON-LD dict
====================================  ===============================  ========================

:func:`skosprovider.extra_data.ignore` can be used as both a loader and a
dumper and is the default everywhere. A new format follows the same rule, so
the extra data of every format can be converted to every other format through
the graph.
