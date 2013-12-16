.. _development:

Development
===========

While skosprovider is still in Alpha development, the basic premise is fairly
stable and the API changes have been fairly minor from version to version.

We try to cover as much code as we can with unit tests. You can run them using
tox_ or directly through nose. When providing a pull request, please run the
unit tests first and make sure they all pass. Please provide new unit tests
to maintain 100% coverage.

.. code-block:: bash

    $ tox
    # No coverage
    $ nosetests 
    # Coverage
    $ nosetests --config nose_cover.cfg

.. _tox: http://tox.testrun.org
