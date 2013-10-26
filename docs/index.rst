.. Skosprovider documentation master file, created by
   sphinx-quickstart on Sun Apr  7 22:37:01 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Skosprovider's documentation!
========================================

Skosprovider provides an interface that can be included in an application to 
allow it to talk to different SKOS vocabularies. These vocabularies could be
defined locally or accessed remotely through webservices.

A sample provider is present in this package, using a simple python dict as
the datastore. Most likely you will want to implement a provider for your own
SKOS, vocabulary or thesaurus system.

Other known providers:
 
* `Skosprovider_oe <https://github.com/koenedaele/skosprovider_oe>`_: This 
  provider implements the :class:`skosprovider.providers.VocabularyProvider` 
  interface for the thesauri deliverd by 
  https://inventaris.onroerenderfgoed.be/thesaurus 
* `Skosprovider_sqlalchemy <http://skosprovider-sqlalchemy.readthedocs.org/en/latest/>`_: 
  An implementation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  interface with a `SQLAlchemy <http://www.sqlalchemy.org>`_ backend.

Contents:

.. toctree::
   :maxdepth: 2

   api
   changes
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

