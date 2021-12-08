1.1.0 (2021-12-08)
------------------

- Last release at this location. Development will move to main Onroerend
  Erfgoed Github account for future versions.
- Allow passing a list of languages to the label function. Eg. passing 
  `['nl-BE', 'en']` will first try to match with any form of Dutch, then any
  form of English and finally anything else. Bear in mind that `nl-BE` will
  also match with `nl`, so passing `['nl-BE', 'nl', 'en']` is superfluous. (#80)
- Better error handling when registering a Conceptscheme with the registry (or
  removing it). (#102)
- Add a CITATION.cff file to make it easier to cite Skosprovider. (#104)

1.0.0 (2021-09-09)
------------------

- Drop support for Python 2. Only version 3.6 and higher are supported now. (#74)
- Remove pyup suspport. (#85)
- Update pyld and other dependencies. (#76)

0.7.1 (2020-05-26)
------------------

- Add check on allowed_instance_scopes being None. (#69)
- Allow getting a provider URI without loading a Conceptscheme. (#72)
- Try not to load the full conceptscheme when registering a provider in the 
  registry. (#72)

0.7.0 (2020-01-19)
------------------

- Add dumpers to transform a provider, a conceptscheme, a concept or
  collection in to a dictionary compatible with a JSON-LD context that has been
  added. This makes it possible to transform a provider into Linked Data.
- Make handling of the hierarchy involving collections as thesaurus arrays more
  logical. A collection now has an attribute 
  :attr:`skosprovider.skos.Collection.infer_concept_relations` that indicates if 
  the members of a collection should be seen as narrower concepts of a superordinate 
  concept. This is generally important when expanding a concept to all it's
  narrower concepts for searching. (#57)
- Add a new query option for querying matches with concepts from external 
  conceptschemes to :meth:`skosprovider.providers.VocabularyProvider.find`.
  (#58)
- A registry can now carry metadata just like a provider.
- A registry now has an attribute
  :attr:`skosprovider.registry.Registry.instance_scope` that indicates how the
  registry is managed in the application process. All providers need to
  indicate what kinds of instance_scope they're compatible with. Especially 
  important for SQLAlchemyProvider run in a web application. (#63, #66)
- Fix a bug that made it impossible for a
  :class:`~skosprovider.providers.SimpleCsvProvider` to read sources. (#36)
- Drop support for Python 3.3, 3.4 and 3.5. Adds support for 3.8. This is the last
  version that will support Python 2. Version 0.8.0 will drop support for
  Python 2.7.

0.6.1 (2017-07-16)
------------------

- A provider can now receive a dataset keyword containing a dict. If present,
  this :class:`dict` needs to have a `uri` attribute.
- Update some requirements.

0.6.0 (2016-08-09)
------------------

- Allow marking a note as containing HTML. (#17)
- Add languages attribute to :class:`skosprovider.skos.ConceptScheme` to make it
  possible to track what languages are being used in a thesaurus. (#19)
- Add a sources attribute to :class:`~skosprovider.skos.ConceptScheme`,
  :class:`~skosprovider.skos.Collection` and
  :class:`~skosprovider.skos.Concept`. Every source is an object that currently
  only has one attribute, a citation. This looks like a good universal common
  denominator. Just as with notes, a citation may contain HTML. (#20, #24)
- Add sorting to :meth:`skosprovider.providers.VocabularyProvider.get_all`,
  :meth:`skosprovider.providers.VocabularyProvider.find`,
  :meth:`skosprovider.providers.VocabularyProvider.get_top_concepts`,
  :meth:`skosprovider.providers.VocabularyProvider.get_top_display`,
  :meth:`skosprovider.providers.VocabularyProvider.get_children_display`.
  Sorting can be done on `id`, `label` or `sortlabel`. The last option makes it
  possible to introduce arbitrary sorting for concepts, eg. to sort periods
  chronologically. The sort order can be specified with the `sort_order`
  parameter. (#21)
- Remove :func:`skosprovider.providers.VocabularyProvider.expand_concept` that
  was deprecated since `0.2.0`.
- Fixed a bug with :func:`skosprovider.skos.dict_to_label` and
  :func:`skosprovider.skos.dict_to_note` that would assign `None` instead of
  `und` as the language for labels and notes that have no language.
- Improved checking for valid URIs with e.g.
  :class:`skosprovider.skos.ConceptScheme`. This was causing weird issues with
  registering a provider to the :class:`skosprovider.registry.Registry`. (#27)

0.5.3 (2015-06-24)
------------------

- When a :class:`skosprovider.providers.DictionaryProvider` reads a dictionary
  containing a :term:`URI` and that URI's None, generate a URI. (#12)
- Upgrade to the newest version of language-tags, this fixes a showstopping bug
  on Windows machines. (#16)
- Added an examples folder with a script that demonstrates the API using a
  DictionaryProvider.
- Added a wheel config file.

0.5.2 (2015-03-02)
------------------

Release 0.5.1 was a brown-paper-bag release due to some mucking about with pypi.

0.5.1 (2015-03-02)
------------------

- Make it possible to pass a language tag to
  :meth:`skosprovider.registry.Registry.find` that will be passed on to all
  relevant registered providers. This determines in what language the
  labels of the returned concepts will displayed. (#10) [dieuska]
- Make it possible to pass a language tag to
  :meth:`skosprovider.registry.Registry.get_all` that will be passed to all
  registered providers. This determines in what language the
  labels of the returned concepts will displayed.
- Fixed some errors with the :func:`skosprovider.utils.dict_dumper`. It didn't
  dump the `matches` or the `subordinate_arrays` of concepts.
- Wrote some new documentation on what a provider is and how to use it. Some
  other documentation work as well such as documenting the `language` parameter
  in the API better.

0.5.0 (2014-12-18)
------------------

- Changed the default language from `None` to the official IANA language code
  `und` (undetermined). This is a minor BC break for users dealing with labels
  that have not been assigned a language.
- Added a :class:`~skosprovider.exceptions.ProviderUnavailableException`
  to let a provider signal that an underlying backend is not available.

0.4.2 (2014-10-16)
------------------

- Fix a problem with SKOS matches.
- BC compatibilty break with 0.4.0 and 0.4.1: renamed the matchtypes broader to
  broad and narrower to narrow to be more inline with the SKOS standard.

0.4.1 (2014-10-15)
------------------

- Made the :class:`~skosprovider.providers.DictionaryProvider` return
  :class:`~skosprovider.skos.Collection` objects with
  :class:`~skosprovider.skos.Note` objects attached if available.
- Fix a problem in find operations when a concept or collection had no label
  attached to it. (#6) [dieuska]

0.4.0 (2014-10-02)
------------------

- Dropped support for Python 2.6 and 3.2.
- Added ability to add :class:`~skosprovider.skos.Note` to
  :class:`~skosprovider.skos.Collection` and
  :class:`~skosprovider.skos.ConceptScheme`.
- Added a :class:`~skosprovider.skos.ConceptScheme` to every provider. This
  ConceptScheme can then be passed on to Concepts and Collections. This allows
  Concepts and Collections that have left the context of their provider, to
  still refer back to the :class:`~skosprovider.skos.ConceptScheme` and thus
  the :class:`skosprovider.providers.VocabularyProvider` where they originated.
- When querying the :class:`~skosprovider.registry.Registry` for providers,
  a :term:`URI` of an accompanying ConceptScheme can now also be used.
- Added :attr:`~skosprovider.skos.Concept.subordinate_arrays` attribute to
  :class:`~skosprovider.skos.Concept` and
  :attr:`~skosprovider.skos.Collection.superordinates` to
  :class:`~skosprovider.skos.Collection`. These attributes are based on the
  :term:`SKOS-THES` specification. They allow linking Concepts and Collections
  for the purpose of displaying a hierarchy.
- Expanded support for languages with
  `language-tags <http://pypi.python.org/pypi/language-tags>`_ library. When
  generating a label, the language specification handles inexact language matches
  better. Eg. when asking for a label with language `nl` for a concept that only
  has `nl-BE` labels, these will now be returned while in the past this was not
  guaranteed.
- Added `subject` to the metadata of a providers. This is a list of subjects
  or tags that help describe or type the provider. The
  :class:`~skosprovider.registry.Registry` can now be searched for
  providers with a certain subject through the
  :meth:`~skosprovider.registry.Registry.get_providers` method.

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
