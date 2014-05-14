0.3.0 (2014-05-14)
------------------

- Added support for :term:`URI`. A :class:`skosprovider.skos.Concept`, 
  :class:`skosprovider.skos.Collection` or 
  :class:`skosprovider.skos.ConceptScheme` can now have a :term:`URI`.
- Query a :class:`skosprovider.providers.VocabularyProvider` or the 
  :class:`skosprovider.registry.Registry` by :term:`URI`.
- Added :mod:`skosprovider.uri` module to handle generating of :term:`URIS <URI>`.
- Added a :meth:`~skosprovider.providers.VocabularyProvider.get_top_concepts`
  method to :class:`skosprovider.providers.VocabularyProvider`. This method
  returns the Top Concepts in a ConceptScheme (the concepts that don't have
  a broader concept).
- Added the :meth:`~skosprovider.providers.VocabularyProvider.get_top_display` 
  and :meth:`~skosprovider.providers.VocabularyProvider.get_children_display`
  methods to handle generating a display hierarchy for a certain provider.
- A method that used to return a list of dicts containing an id and a label, 
  now also returns a uri and a type (concept/collection) for each dict. (#2)
- Provide list of valid noteTypes and labelTypes as attributes of Note and 
  Label so they can be used externally. (#4)
- Reworking tests. Now using pytest in stead of nose.
- Adding code coverage based on `Coveralls <https://coveralls.io>`_.

0.2.1 (2013-12-06)
------------------

- Make the :class:`skosprovider.providers.MemoryProvider` forward compatible
  by constructing :class:`skosprovider.skos.Concept` and 
  :class:`skosprovider.skos.Collection` objects with keywords.
- Soms minor fixes in documentation.
- Added an extra unit test.

0.2.0 (2013-05-16)
------------------

- Major rewrite and refactoring. Tried to keep BC in place as much as possible,
  but did change some stuff.
- Added a read only SKOS domain model in the :mod:`skosprovider.skos` module.
- Providers no longer return dicts as concepts, but instances of 
  :class:`skosprovider.skos.Concept`.
- Added support for skos collections with a 
  :class:`skosprovider.skos.Collection` object.
- Expanded concept query syntax. Now allows for querying on type 
  (concept or collection) and on collection membership. See 
  :meth:`skosprovider.providers.VocabularyProvider.find`.
- Added :func:`skosprovider.utils.dict_dumper`.

0.1.3 (2013-03-22)
------------------

- Find empty label now returns no results
- Find without a label now calls get_all

0.1.2 (2013-02-07)
------------------

- Providers can be removed from the registry
- Added the ability to get a single provider from the registry
- No longer possible to register the same provider twice

0.1.1 (2012-12-11)
------------------

- Some pep8 fixes
- Add support for tox
- Now tested for python 3.2
- Added skos:notes as an example to the unit tests.

0.1.0
-----

- Initial version
