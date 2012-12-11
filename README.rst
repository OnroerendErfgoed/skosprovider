skosprovider: vocabulary abstraction
====================================

This library helps abstract vocabularies that stick to the SKOS specification.

.. image:: https://secure.travis-ci.org/koenedaele/skosprovider.png
        :target: https://secure.travis-ci.org/koenedaele/skosprovider

Skosprovider provides an interface that can be included in an application to 
allow it to talk to different SKOS vocabularies. These vocabularies could be
defined locally or accessed remotely through webservices.

A sample provider is present in this package, using a simple python dict as
the datastore. Most likely you will want to implement a provider for your own
SKOS, vocabulary or thesaurus system.

Other known providers:
 
* https://github.com/koenedaele/skosprovider_oe: This providers implements the 
  provider interface for the thesauri deliverd by 
  https://inventaris.onroerenderfgoed.be/thesaurus 
