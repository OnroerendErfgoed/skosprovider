.. _introduction:

Introduction
============

Skosprovider provides an interface that can be included in an application to 
allow it to talk to different :term:`SKOS` vocabularies. These vocabularies could be
defined locally or accessed remotely through webservices.

Adhering to this interface in you application decouples your application and the
actual thesaurus. This makes unit testing easy because it allows you to swap
a remote and a local implementation. It also makes it easy to switch from a 
simple, static implementation based on a csv file to a more complete implementation
using you relation database.

One of the main goals of this project is to be able to build an application that
can use thesauri or vocabularies without knowing upfront what these might be
or where they might come from. This could be for an application that allows
cataloguing things, but where it can be expected that different instances will
require different thesauri or would need to be able to talk to existing vocabulary
systems.

Some sample providers are present in this package. The 
:class:`skosprovider.providers.DictionaryProvider` uses a simple python dict 
as the datastore. It can be considered the reference implementation for the 
:class:`skosprovider.providers.VocabularyProvider` interface. Most likely you 
will want to implement a provider for your own SKOS, vocabulary or 
thesaurus system.

Other providers
---------------

Currently the following other providers exist:
 
* `Skosprovider_oe <https://github.com/koenedaele/skosprovider_oe>`_: This 
  provider implements the :class:`skosprovider.providers.VocabularyProvider` 
  interface for the thesauri attached to the 
  `Inventaris Onroerend Erfgoed <https://inventaris.onroerenderfgoed.be/thesaurus>`_.
  It also demonstrates making the switch from a term based thesaurus to a 
  concept based one.
* `Skosprovider_sqlalchemy <http://skosprovider-sqlalchemy.readthedocs.org/en/latest/>`_: 
  An implementation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  interface with a `SQLAlchemy <http://www.sqlalchemy.org>`_ backend. This allows
  using a RDBMS for reading, but also writing, :term:`SKOS` concepts.
* `Skosprovider_rdf <http://skosprovider-rdf.readthedocs.org/en/latest/>`_:
  An implementation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  interface with a `RDFLib <https://rdflib.readthedocs.org/en/latest/>`_ 
  backend. This allows using a SKOS RDf file as the source for a provider, 
  but also dumping a skosprovider to a SKOS RDF file.

There also exists a library to integrate Skosprovider with
`Pyramid <http://www.pylonsproject.org/>`_ at 
`pyramid_skosprovider <https://github.com/koenedaele/pyramid_skosprovider>`_.

Deviations from SKOS
--------------------

In a few places we've deviated a bit from the :term:`SKOS` standard:

* While :term:`SKOS` technically allows for things like a broader/narrower
  relation between `concepts` in different `conceptschemes`, Skosprovider 
  assumes that all hierarchical or associative relations should be between
  `concepts` in the same `conceptscheme`. For relations between concepts in
  different schemes, the :term:`SKOS` mappings should be considered.
* The :term:`SKOS` standard allows a `concept` that is marked as a `topConcept` 
  to have a broader `concept`. Skosprovider expects that the concepts returned
  by the :meth:`skosprovider.providers.VocabularyProvider.get_top_concepts` do
  not have any broader concepts.
* The SKOS ontology ony describes a SKOS:member predicate to indicate that a
  collection has certain members. There's an implicit reverse side to this 
  relation (eg. a concept is a member of a collection). We've standardised this
  on the member_of property that's available on a 
  :class:`skosprovider.skos.Concept` and a :class:`skosprovider.skos.Collection`.
