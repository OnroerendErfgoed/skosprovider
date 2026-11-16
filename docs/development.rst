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
