.. _development:

Development
===========

While skosprovider is still in development, the basic premise is fairly
stable and the API changes have been fairly minor from version to version. We do
continue to refine the project and make the providers more expressive.

We try to cover as much code as we can with unit tests. You can run them using
tox_ or directly through nose. When providing a pull request, please run the
unit tests first and make sure they all pass. Please provide new unit tests
to maintain 100% coverage.

.. code-block:: bash

    $ tox
    # No coverage
    $ py.test 
    # Coverage
    $ py.test --cov skosprovider --cov-report term-missing
    # Only run a subset of the tests
    $ py.test skosprovider/tests/test_registry.py

.. _tox: http://tox.testrun.org
