skosprovider: vocabulary abstraction
====================================

This library helps abstract vocabularies that stick to the SKOS specification.

.. image:: https://travis-ci.org/koenedaele/skosprovider.png?branch=master
        :target: https://travis-ci.org/koenedaele/skosprovider
.. image:: https://coveralls.io/repos/koenedaele/skosprovider/badge.png?branch=master
        :target: https://coveralls.io/r/koenedaele/skosprovider
.. image:: https://badge.fury.io/py/skosprovider.png
        :target: http://badge.fury.io/py/skosprovider

Building the docs
-----------------

More information about this library can be found in :file:`docs`. The docs can be 
built using `Sphinx <http://sphinx-doc.org>`_.

Please make sure you have installed Sphinx in the same environment where 
skosprovider is present.

.. code-block:: bash

    # activate your virtual env
    $ pip install sphinx
    $ python setup.py develop
    $ cd docs
    $ make html
