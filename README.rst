skosprovider: vocabulary abstraction
====================================

This library helps abstract vocabularies (thesauri, controlled lists, authority
files). It depends heavily on the 
`SKOS <http://www.w3.org/2004/02/skos>`_ specification, but adds elements
of other specifications such as the 
`ISO 25964 SKOS extension <http://pub.tenforce.com/schemas/iso25964/skos-thes/>`_ 
where deemed useful.

.. image:: https://app.travis-ci.com/koenedaele/skosprovider.svg?branch=master
    :target: https://app.travis-ci.com/koenedaele/skosprovider
.. image:: https://coveralls.io/repos/koenedaele/skosprovider/badge.svg?branch=master
        :target: https://coveralls.io/github/koenedaele/skosprovider?branch=master
.. image:: https://scrutinizer-ci.com/g/koenedaele/skosprovider/badges/quality-score.png?b=master
        :target: https://scrutinizer-ci.com/g/koenedaele/skosprovider/?branch=master

.. image:: https://readthedocs.org/projects/skosprovider/badge/?version=latest
        :target: https://readthedocs.org/projects/skosprovider/?badge=latest
.. image:: https://badge.fury.io/py/skosprovider.png
        :target: http://badge.fury.io/py/skosprovider

Building the docs
-----------------

More information about this library can be found in `docs`. The docs can be 
built using `Sphinx <http://sphinx-doc.org>`_.

Please make sure you have installed Sphinx in the same environment where 
skosprovider is present.

.. code-block:: bash

    # activate your virtual env
    $ pip install -r requirements.txt
    $ python setup.py develop
    $ cd docs
    $ make html
