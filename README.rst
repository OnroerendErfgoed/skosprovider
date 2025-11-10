skosprovider: vocabulary abstraction
====================================

This library helps abstract vocabularies (thesauri, controlled lists, authority
files). It depends heavily on the 
`SKOS <http://www.w3.org/2004/02/skos>`_ specification, but adds elements
of other specifications such as the 
`ISO 25964 SKOS extension <http://pub.tenforce.com/schemas/iso25964/skos-thes/>`_ 
where deemed useful.

.. image:: https://img.shields.io/pypi/v/skosprovider.svg
    :target: https://pypi.python.org/pypi/skosprovider
.. image:: https://readthedocs.org/projects/skosprovider/badge/?version=latest
    :target: https://readthedocs.org/projects/skosprovider/?badge=latest
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5767151.svg
    :target: https://doi.org/10.5281/zenodo.5767151
.. image:: https://app.travis-ci.com/onroerenderfgoed/skosprovider.svg?branch=develop
    :target: https://app.travis-ci.com/onroerenderfgoed/skosprovider
.. image:: https://coveralls.io/repos/OnroerendErfgoed/skosprovider/badge.svg?branch=develop
    :target: https://coveralls.io/github/OnroerendErfgoed/skosprovider?branch=develop
.. image:: https://scrutinizer-ci.com/g/onroerenderfgoed/skosprovider/badges/quality-score.png?b=develop
    :target: https://scrutinizer-ci.com/g/onroerenderfgoed/skosprovider/?branch=develop

Building the docs
-----------------

More information about this library can be found in `docs`. The docs can be 
built using `Sphinx <http://sphinx-doc.org>`_.

Please make sure you have installed Sphinx in the same environment where 
skosprovider is present.

.. code-block:: bash

    # activate your virtual environment
    $ pip install -r requirements.txt
    $ python setup.py develop
    $ cd docs
    $ make html

