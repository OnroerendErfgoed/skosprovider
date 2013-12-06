0.2.1 (2013-12-06)
------------------

- Make the :class:'skosprovider.providers.MemoryProvider` forward compatible
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
