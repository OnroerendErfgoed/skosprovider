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
using your relation database of choice.

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
 
* `Skosprovider_sqlalchemy <http://skosprovider-sqlalchemy.readthedocs.org/en/latest/>`_: 
  An implementation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  interface with a `SQLAlchemy <http://www.sqlalchemy.org>`_ backend. This allows
  using a RDBMS for reading, but also writing, :term:`SKOS` concepts.
* `Skosprovider_rdf <http://skosprovider-rdf.readthedocs.org/en/latest/>`_:
  An implementation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  interface with a `RDFLib <https://rdflib.readthedocs.org/en/latest/>`_ 
  backend. This allows using a SKOS RDF file as the source for a provider, 
  but also dumping a skosprovider to a SKOS RDF file.
* `Skosprovider_atramhasis <https://skosprovider-atramhasis.readthedocs.org>`_:
  The :class:`AtramhasisProvider <skosprovider.providers.AtramhasisProvider>` 
  lets you interact with an Atramhasis_ instance. 
* `Skosprovider_getty <http://skosprovider-getty.readthedocs.org/en/latest/>`_:
  An implemenation of the 
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` 
  against the Linked Open Data vocabularies published by the Getty Research 
  Institute at `http://vocab.getty.edu <http://vocab.getty.edu>`_ such as the
  `Art and Architecture Thesaurus (AAT)` and the 
  `Thesaurus of Geographic Names (TGN)`.
* `Skosprovider_heritagedata <http://skosprovider-heritagedata.readthedocs.org>`_:
  An implementation of the
  :class:`VocabularyProvider <skosprovider.providers.VocabularyProvider>` against
  the vocabularies published by EH, RCAHMS and RCAHMW at 
  `heritagedata.org <http://heritagedata.org>`_.

There also exists a library to integrate Skosprovider with
`Pyramid <http://www.pylonsproject.org/>`_ at 
`pyramid_skosprovider <https://github.com/onroerenderfgoed/pyramid_skosprovider>`_.
This allows you to embed a set of REST services in a Pyramid application that
expose SKOSproviders as JSON services that can be consumed by eg. Javascript 
clients or other clients.

For those who are looking to build a vocabulary, there's also Atramhasis_, 
an online :term:`SKOS` vocabulary editor that builds upon this library and 
others. Atramhasis can function as the central SKOS registry for an organisation 
looking to manage its own thesauri and other controlled vocabularies. It 
provides a public website that allows people to browse you vocabularies and 
a private interface that allows vocabulary editors to create, edit and delete 
concepts and collections. By using other Skosproviders Atramhasis can import 
concepts and collections from other thesauri, saving you the trouble of having 
to write your own controlled vocabulary from scratch.

Deviations from SKOS
--------------------

In a few places we've deviated a bit from the :term:`SKOS` standard:

* While :term:`SKOS` technically allows for things like a broader/narrower
  relation between `concepts` in different `conceptschemes`, Skosprovider 
  assumes that all hierarchical or associative relations should be between
  `concepts` in the same `conceptscheme`. For relations between concepts in
  different schemes, the :term:`SKOS` mapping properties (skos:mappingRelation,
  skos:closeMatch, skos:exactmatch, ...) should be used. These are supported
  by Skosprovider since version 0.4.0.
* The :term:`SKOS` standard allows a `concept` that is marked as a `topConcept` 
  to have a broader `concept`. Skosprovider expects that the concepts returned
  by the :meth:`skosprovider.providers.VocabularyProvider.get_top_concepts` do
  not have any broader concepts.
* The SKOS ontology ony describes a SKOS:member predicate to indicate that a
  collection has certain members. There's an implicit reverse side to this 
  relation (eg. a concept is a member of a collection). We've standardised this
  on the member_of property that's available on a 
  :class:`skosprovider.skos.Concept` and a :class:`skosprovider.skos.Collection`.
* SKOS provides no way for specifying where in a hierarchy a 
  :class:`skosprovider.skos.Collection` should be placed. Since this is a fairly
  standard requirement for most thesauri, we have implemented this by looking
  at the :term:`SKOS-THES` specification. We have borrowed the 
  :attr:`skosprovider.skos.Concept.subordinate_arrays` and 
  :attr:`skosprovider.skos.Collection.superordinates` properties from this
  specification. In effect, it turns a SKOS Collection that has one or more 
  superordinates into a ThesaurusArray. Since `0.7.0` it's possible to
  explicitly state if the member of a collection that has a superordinate
  concept should be seen as narrower concepts of that superordinate concept
  with the :attr:`skosprovider.skos.Collection.infer_concept_relations`. By
  default this is set to True. If you want to model a collection that does not
  contain narrower concepts of it's superordinate, set it to False. This will
  mainly stop search expansion using the
  :meth:`skosprovider.providers.VocabularyProvider.expand` method.

Support
-------

If you have questions regarding Skosprovider, feel free to contact us. Any bugs
you find or feature requests you have, you can add to our 
`issue tracker <https://github.com/onroerenderfgoed/skosprovider/issues>`_. If you're
unsure if something is a bug or intentional, or you just want to have a chat
about this library or :term:`SKOS` in general, feel free to join the 
`Atramhasis discussion forum <https://groups.google.com/forum/#!forum/atramhasis>`_.
While these are separate software projects, they are being run by the same 
people and they integrate rather tightly.

.. _Atramhasis: http://atramhasis.readthedocs.org
