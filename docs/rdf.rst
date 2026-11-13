.. _rdf:

RDF
===

The :mod:`skosprovider.rdf` package reads :term:`SKOS` from and writes
:term:`SKOS` to an :class:`rdflib.graph.Graph`. It used to be the separate
``skosprovider_rdf`` package. See :ref:`rdf_migration` when upgrading from
that package.

Loading a graph
---------------

The :class:`~skosprovider.rdf.provider.RDFProvider` is an implementation of
the :class:`~skosprovider.provider.VocabularyProvider` interface that uses an
:class:`rdflib.graph.Graph` as input. This provider can be used to add a
:term:`SKOS` vocabulary contained in an :term:`RDF` file to your application.
The provider itself does not read the file, but expects to be passed a
:class:`~rdflib.graph.Graph`. So any :term:`RDF` serialisation that can be
read by :mod:`rdflib` can be used with this provider.

.. literalinclude:: /../examples/rdf/load_skos.py
    :language: python

The provider reads the whole graph when it is constructed and keeps the
concepts and collections in memory, so it is best suited for small to
medium-sized vocabularies. The graph itself is not kept and can be garbage
collected afterwards.

The id of a concept or collection is read from ``dcterms:identifier`` or
``dc:identifier``. When neither is present, the :term:`URI` is used as id.

Picking a concept scheme
------------------------

A provider represents exactly one concept scheme. The provider picks it as
follows:

* When a :class:`~skosprovider.skos.ConceptScheme` is passed through the
  ``concept_scheme`` parameter, that concept scheme is used.
* When the :term:`URI` of a concept scheme is passed through the
  ``concept_scheme_uri`` parameter, that concept scheme is read from the
  graph. A :class:`~skosprovider.exceptions.ConceptSchemeException` is raised
  when the graph does not contain it.
* Otherwise, when the graph contains exactly one ``skos:ConceptScheme``, that
  one is used. When it contains none, a concept scheme with a :term:`URN`
  based on the id of the provider is created. When it contains more than one,
  a :class:`~skosprovider.exceptions.ConceptSchemeException` is raised and you
  have to pick one with one of the parameters above.

When you specify a concept scheme with one of the parameters, only the
concepts and collections linked to it through ``skos:inScheme`` or
``skos:topConceptOf`` are loaded.

.. literalinclude:: /../examples/rdf/load_specific_scheme.py
    :language: python

Labels, notes and sources
-------------------------

Labels can be plain :term:`SKOS` labels (``skos:prefLabel``,
``skos:altLabel`` and ``skos:hiddenLabel``) or :term:`SKOS-XL` labels
(``skosxl:prefLabel``, ``skosxl:altLabel`` and ``skosxl:hiddenLabel``). A
:term:`SKOS-XL` label with a :term:`URI` becomes a
:class:`~skosprovider.skos.Label` with that :term:`URI`, its
``skosxl:literalForm`` as text and its ``dcterms:type`` values as
:attr:`~skosprovider.skos.Label.label_types`. A :term:`SKOS-XL` label that is
a blank node becomes a plain label. When a plain label and a :term:`SKOS-XL`
label of the same type have the same text and language, only the
:term:`SKOS-XL` label is kept.

A note is either a literal or a node with its text under ``rdf:value``. A
note node with a :term:`URI` becomes a :class:`~skosprovider.skos.Note` with
that :term:`URI`. Literals typed as ``rdf:HTML`` become notes with HTML
markup.

A source is a ``dcterms:source`` with its citation under
``dcterms:bibliographicCitation`` or ``rdf:value``.

Dumping a provider
------------------

The :mod:`skosprovider.rdf.dumper` module dumps any implementation of
:class:`~skosprovider.provider.VocabularyProvider` to an
:class:`rdflib.graph.Graph`. Since only the
:class:`~rdflib.graph.Graph` is dealt with, a provider can be serialised to
any :term:`RDF` serialisation :mod:`rdflib` supports.

* :func:`~skosprovider.rdf.dumper.rdf_dumper` dumps the concept scheme and
  all concepts and collections of a provider.
* :func:`~skosprovider.rdf.dumper.rdf_conceptscheme_dumper` dumps only the
  concept scheme, with its top concepts.
* :func:`~skosprovider.rdf.dumper.rdf_concept_or_collection_dumper` dumps a
  single concept or collection, together with its concept scheme.

.. literalinclude:: /../examples/rdf/dump.py
    :language: python

A label with a :term:`URI` is dumped as a :term:`SKOS-XL` label, any other
label as a plain :term:`SKOS` label. A ``sortLabel`` has no :term:`SKOS`
counterpart and is dumped as a ``skos:hiddenLabel``. A note with a
:term:`URI` is dumped as a node with its text under ``rdf:value``, any other
note as a literal.

When the members of a collection with
:attr:`~skosprovider.skos.Collection.infer_concept_relations` set are
narrower concepts of its superordinates, the dumpers add the inferred
``skos:broader`` and ``skos:narrower`` relations.

Extra data
----------

:class:`~skosprovider.rdf.provider.RDFProvider` takes an optional
``extra_data_loader`` and the dumpers take an optional
``extra_data_dumper``. They default to
:func:`~skosprovider.extra_data.ignore`.

The loader receives the graph and the node of an object and returns an
:class:`rdflib.Graph` or `None`, which becomes the
:attr:`~skosprovider.skos.Concept.extra_data` of that object. The dumper
receives an object and returns an :class:`rdflib.Graph` or `None`, which is
merged into the dump together with its namespace bindings.

:mod:`skosprovider.rdf.extra_data` has a ready-made loader and dumper:
:func:`~skosprovider.rdf.extra_data.from_unmapped` keeps the triples that
:class:`~skosprovider.rdf.provider.RDFProvider` does not turn into attributes,
eg. a ``skos:notation`` or a ``dct:creator``, and
:func:`~skosprovider.rdf.extra_data.to_unmapped` writes them to the dump again.

Extra data is supported for the concept scheme, concepts and collections, and
for sources, labels and notes with a :term:`URI`. A blank node has no identity
outside the graph it was read from, so a source, label or note without a
:term:`URI` gets no extra data: the loader and the dumper are not called for
it.

.. code-block:: python

    from skosprovider.rdf.dumper import rdf_dumper
    from skosprovider.rdf.extra_data import from_unmapped
    from skosprovider.rdf.extra_data import to_unmapped
    from skosprovider.rdf.provider import RDFProvider

    provider = RDFProvider({"id": "TREES"}, graph, extra_data_loader=from_unmapped)
    dump = rdf_dumper(provider, extra_data_dumper=to_unmapped)

Errors raised by a loader or dumper are wrapped in an
:class:`~skosprovider.exceptions.ExtraDataException`, with notes describing
which object was being processed.

.. _rdf_migration:

Migrating from skosprovider_rdf
-------------------------------

The ``skosprovider_rdf`` package has been merged into skosprovider 2.0.0 as
:mod:`skosprovider.rdf`. The ``skosprovider_rdf`` package remains usable with
``skosprovider < 2.0.0``, but is no longer maintained.

* Imports move from ``skosprovider_rdf.providers`` to
  :mod:`skosprovider.rdf.provider` and from ``skosprovider_rdf.utils`` to
  :mod:`skosprovider.rdf.dumper`. :class:`~skosprovider.rdf.provider.RDFProvider`
  and the dumpers can also be imported from :mod:`skosprovider.rdf` directly.
* ``rdf_c_dumper(provider, c)`` is renamed to
  :func:`rdf_concept_or_collection_dumper(provider, id_)
  <skosprovider.rdf.dumper.rdf_concept_or_collection_dumper>`. It raises a
  :class:`~skosprovider.exceptions.NotFoundException` instead of an
  :class:`AttributeError` for an unknown id.
* When dumping, unknown ids in relations and ids that point to the wrong type
  (eg. a concept in the ``member_of`` of a concept) are skipped instead of
  raising an :class:`AttributeError`.
* :class:`~skosprovider.rdf.provider.RDFProvider` raises a
  :class:`~skosprovider.exceptions.ConceptSchemeException` instead of a
  :class:`RuntimeError` when it can not pick a concept scheme, and an
  :class:`~skosprovider.exceptions.InvalidDataException` instead of a
  :class:`ValueError` for an invalid label or note type. They extend
  :class:`RuntimeError` and :class:`ValueError`, so existing ``except``
  clauses keep working.
* A ``concept_scheme_uri`` that does not match a concept scheme in the graph
  now raises a :class:`~skosprovider.exceptions.ConceptSchemeException`, also
  when the graph contains one or no concept scheme. It used to be ignored in
  those cases.
* :class:`~skosprovider.rdf.provider.RDFProvider` no longer keeps the graph
  it is built from: the ``graph`` attribute is removed. The
  ``check_in_scheme`` class attribute is removed, the instance attribute is
  unchanged.
* The ``member_of`` of concepts and collections follows the order of the
  collections in the graph instead of an arbitrary order.
* :term:`SKOS-XL` labels and note nodes are read instead of being ignored,
  and labels with a :term:`URI` are dumped as :term:`SKOS-XL` labels.
