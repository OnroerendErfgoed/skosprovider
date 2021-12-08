# -*- coding: utf-8 -*-

'''
This module contains a read-only model of the :term:`SKOS` specification.

To complement the :term:`SKOS` specification, some elements were borrowed
from the :term:`SKOS-THES` specification (eg. superordinate and
subordinate array).

.. versionadded:: 0.2.0
'''

from language_tags import tags

from .uri import is_uri

valid_markup = [
    None,
    'HTML'
]
'''
Valid types of markup for a note or a source.
'''


class Label:
    '''
    A :term:`SKOS` Label.
    '''

    label = None
    '''
    The label itself (eg. `churches`, `trees`, `Spitfires`, ...)
    '''

    type = "prefLabel"
    '''
    The type of this label (`prefLabel`, `altLabel`, `hiddenLabel`, 'sortLabel').
    '''

    language = "und"
    '''
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    '''

    valid_types = [
        'prefLabel',
        'altLabel',
        'hiddenLabel',
        'sortLabel'
    ]
    '''
    The valid types for a label
    '''

    def __init__(self, label, type="prefLabel", language="und"):
        self.label = label
        self.type = type
        if not language:
            language = 'und'
        if tags.check(language):
            self.language = language
        else:
            raise ValueError('%s is not a valid IANA language tag.' % language)

    def __eq__(self, other):
        return self.__dict__ == (other if type(other) == dict else other.__dict__)

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def is_valid_type(type):
        '''
        Check if the argument is a valid SKOS label type.

        :param string type: The type to be checked.
        '''
        return type in Label.valid_types

    def __repr__(self):
        return "Label('%s', '%s', '%s')" % (self.label, self.type, self.language)


class Note:
    '''
    A :term:`SKOS` Note.
    '''

    note = None
    '''The note itself'''

    type = "note"
    '''
    The type of this note ( `note`, `definition`, `scopeNote`, ...).
    '''

    language = "und"
    '''
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    '''

    markup = None
    '''
    What kind of markup does the note contain?

    If not `None`, the note should be treated as a certain type of markup.
    Currently only HTML is allowed.
    '''

    valid_types = [
            'note',
            'changeNote',
            'definition',
            'editorialNote',
            'example',
            'historyNote',
            'scopeNote'
        ]
    '''
    The valid types for a note.
    '''

    def __init__(self, note, type="note", language="und", markup=None):
        self.note = note
        self.type = type
        if not language:
            language = 'und'
        if tags.check(language):
            self.language = language
        else:
            raise ValueError('%s is not a valid IANA language tag.' % language)
        if self.is_valid_markup(markup):
            self.markup = markup
        else:
            raise ValueError('%s is not valid markup.' % markup)

    def __eq__(self, other):
        return self.__dict__ == (other if type(other) == dict else other.__dict__)

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def is_valid_type(type):
        '''
        Check if the argument is a valid SKOS note type.

        :param string type: The type to be checked.
        '''
        return type in Note.valid_types

    @staticmethod
    def is_valid_markup(markup):
        '''
        Check the argument is a valid type of markup.

        :param string markup: The type to be checked.
        '''
        return markup in valid_markup


class Source:
    '''
    A `Source` for a concept, collection or scheme.

    '''

    citation = None
    '''A bibliographic citation for this source.'''

    markup = None
    '''
    What kind of markup does the source contain?

    If not `None`, the source should be treated as a certain type of markup.
    Currently only HTML is allowed.
    '''

    def __init__(self, citation, markup=None):
        self.citation = citation
        if self.is_valid_markup(markup):
            self.markup = markup
        else:
            raise ValueError('%s is not valid markup.' % markup)

    @staticmethod
    def is_valid_markup(markup):
        '''
        Check the argument is a valid type of markup.

        :param string markup: The type to be checked.
        '''
        return markup in valid_markup


class ConceptScheme:
    '''
    A :term:`SKOS` ConceptScheme.

    :param string uri: A :term:`URI` for this conceptscheme.
    :param list labels: A list of :class:`skosprovider.skos.Label` instances.
    :param list notes: A list of :class:`skosprovider.skos.Note` instances.
    '''

    uri = None
    '''A :term:`URI` for this conceptscheme.'''

    labels = []
    '''A :class:`lst` of :class:`skosprovider.skos.label` instances.'''

    notes = []
    '''A :class:`lst` of :class:`skosprovider.skos.Note` instances.'''

    sources = []
    '''A :class:`lst` of :class:`skosprovider.skos.Source` instances.'''

    languages = []
    '''
    A :class:`lst` of languages that are being used in the ConceptScheme.

    There's no guarantuee that labels or notes in other languages do not exist.
    '''

    def __init__(self, uri, labels=[], notes=[], sources=[], languages=[]):
        if not is_uri(uri):
            raise ValueError('%s is not a valid URI.' % uri)
        self.uri = uri
        self.labels = [dict_to_label(l) for l in labels]
        self.notes = [dict_to_note(n) for n in notes]
        self.sources = [dict_to_source(s) for s in sources]
        self.languages = languages

    def label(self, language='any'):
        '''
        Provide a single label for this conceptscheme.

        This uses the :func:`label` function to determine which label to
        return.

        :param string language: The preferred language to receive the label in.
            This should be a valid IANA language tag.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        '''
        return label(self.labels, language)

    def _sortkey(self, key='uri', language='any'):
        '''
        Provide a single sortkey for this conceptscheme.

        :param string key: Either `uri`, `label` or `sortlabel`.
        :param string language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
        :rtype: :class:`str`
        '''
        if key == 'uri':
            return self.uri
        else:
            l = label(self.labels, language, key == 'sortlabel')
            return l.label.lower() if l else ''

    def __repr__(self):
        return "ConceptScheme('%s')" % self.uri


class Concept:
    '''
    A :term:`SKOS` Concept.
    '''

    id = None
    '''An id for this Concept within a vocabulary

    eg. 12345
    '''

    uri = None
    '''A proper uri for this Concept

    eg. `http://id.example.com/skos/trees/1`
    '''

    type = 'concept'
    '''The type of this concept or collection.

    eg. 'concept'
    '''

    concept_scheme = None
    '''The :class:`ConceptScheme` this Concept is a part of.'''

    labels = []
    '''A :class:`lst` of :class:`Label` instances.'''

    notes = []
    '''A :class:`lst` of :class:`Note` instances.'''

    sources = []
    '''A :class:`lst` of :class:`skosprovider.skos.Source` instances.'''

    broader = []
    '''A :class:`lst` of concept ids.'''

    narrower = []
    '''A :class:`lst` of concept ids.'''

    related = []
    '''A :class:`lst` of concept ids.'''

    member_of = []
    '''A :class:`lst` of collection ids.'''

    subordinate_arrays = []
    '''A :class:`list` of collection ids.'''

    matches = {},
    '''
    A :class:`dictionary`. Each key is a matchtype and contains a :class:`list` of URI's.
    '''

    matchtypes = [
        'close',
        'exact',
        'related',
        'broad',
        'narrow'
    ]
    '''Matches with Concepts in other ConceptSchemes.

    This dictionary contains a key for each type of Match (close, exact,
    related, broad, narrow). Attached to each key is a list of URI's.
    '''

    def __init__(self, id, uri=None,
                 concept_scheme=None,
                 labels=[], notes=[], sources=[],
                 broader=[], narrower=[], related=[],
                 member_of=[], subordinate_arrays=[],
                 matches={}):
        self.id = id
        self.uri = uri
        self.type = 'concept'
        self.concept_scheme = concept_scheme
        self.labels = [dict_to_label(l) for l in labels]
        self.notes = [dict_to_note(n) for n in notes]
        self.sources = [dict_to_source(s) for s in sources]
        self.broader = broader
        self.narrower = narrower
        self.related = related
        self.member_of = member_of
        self.subordinate_arrays = subordinate_arrays
        self.matches = {key: [] for key in self.matchtypes}
        self.matches.update(matches)

    def label(self, language='any'):
        '''
        Provide a single label for this concept.

        This uses the :func:`label` function to determine which label to return.

        :param string language: The preferred language to receive the label in.
            This should be a valid IANA language tag or a list of language tags.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        '''
        return label(self.labels, language)

    def _sortkey(self, key='id', language='any'):
        '''
        Provide a single sortkey for this collection.

        :param string key: Either `id`, `uri`, `label` or `sortlabel`.
        :param string language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
        :rtype: :class:`str`
        '''
        if key == 'id':
            return str(self.id)
        elif key == 'uri':
            return self.uri if self.uri else ''
        else:
            l = label(self.labels, language, key == 'sortlabel')
            return l.label.lower() if l else ''

    def __repr__(self):
        return "Concept('%s')" % self.id


class Collection:
    '''
    A :term:`SKOS` Collection.
    '''

    id = None
    '''An id for this Collection within a vocabulary'''

    uri = None
    '''A proper uri for this Collection'''

    type = 'collection'
    '''The type of this concept or collection.

    eg. 'collection'
    '''

    concept_scheme = None
    '''The :class:`ConceptScheme` this Collection is a part of.'''

    labels = []
    '''A :class:`lst` of :class:`skosprovider.skos.label` instances.'''

    notes = []
    '''A :class:`lst` of :class:`skosprovider.skos.Note` instances.'''

    sources = []
    '''A :class:`lst` of :class:`skosprovider.skos.Source` instances.'''

    members = []
    '''A :class:`lst` of concept or collection ids.'''

    member_of = []
    '''A :class:`lst` of collection ids.'''

    superordinates = []
    '''A :class:`lst` of concept ids.'''

    infer_concept_relations = True
    '''Should member concepts of this collection be seen as narrower concept of
    a superordinate of the collection?'''

    def __init__(self, id, uri=None,
                 concept_scheme=None,
                 labels=[], notes=[], sources=[],
                 members=[], member_of=[],
                 superordinates=[],
                 infer_concept_relations=True):
        self.id = id
        self.uri = uri
        self.type = 'collection'
        self.concept_scheme = concept_scheme
        self.labels = [dict_to_label(l) for l in labels]
        self.notes = [dict_to_note(n) for n in notes]
        self.sources = [dict_to_source(s) for s in sources]
        self.members = members
        self.member_of = member_of
        self.superordinates = superordinates
        self.infer_concept_relations = infer_concept_relations

    def label(self, language='any'):
        '''
        Provide a single label for this collection.

        This uses the :func:`label` function to determine which label to return.

        :param string language: The preferred language to receive the label in.
            This should be a valid IANA language tag.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        '''
        return label(self.labels, language, False)

    def _sortkey(self, key='id', language='any'):
        '''
        Provide a single sortkey for this collection.

        :param string key: Either `id`, `uri`, `label` or `sortlabel`.
        :param string language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
        :rtype: :class:`str`
        '''
        if key == 'id':
            return str(self.id)
        elif key == 'uri':
            return self.uri if self.uri else ''
        else:
            l = label(self.labels, language, key == 'sortlabel')
            return l.label.lower() if l else ''

    def __repr__(self):
        return "Collection('%s')" % self.id


def label(labels=[], language='any', sortLabel=False):
    '''
    Provide a label for a list of labels.

    The items in the list of labels are assumed to be either instances of
    :class:`Label`, or dicts with at least the key `label` in them. These will
    be passed to the :func:`dict_to_label` function.

    This method tries to find a label by looking if there's
    a pref label for the specified language. If there's no pref label,
    it looks for an alt label. It disregards hidden labels.

    While matching languages, preference will be given to exact matches. But,
    if no exact match is present, an inexact match will be attempted. This might
    be because a label in language `nl-BE` is being requested, but only `nl` or
    even `nl-NL` is present. Similarly, when requesting `nl`, a label with
    language `nl-NL` or even `nl-Latn-NL` will also be considered,
    providing no label is present that has an exact match with the
    requested language.

    It's possible to pass multiple languages as a list. In this case, the method
    will try handling each language in turn. Please be aware that this includes
    handling variations. When assing `nl-BE, nl, nl-NL`, the second and third
    languages will never be handled since handling `nl-BE` includes looking for
    other related languages such as `nl-NL` and `nl`.

    If language 'any' was specified, all labels will be considered,
    regardless of language.

    To find a label without a specified language, pass `None` as language.

    If a language or None was specified, and no label could be found, this
    method will automatically try to find a label in some other language.

    Finally, if no label could be found, None is returned.

    ..versionchanged:: 1.1
        It is now possible to pass a list of languages.

    :param any language: The preferred language to receive the label in. This
        should be a valid IANA language tag or list of language tags. If you
        pass a list, the order of the languages in the list will be taken into
        account when trying to determine a label.
    :param boolean sortLabel: Should sortLabels be considered or not? If True,
        sortLabels will be preferred over prefLabels. Bear in mind that these
        are still language dependent. So, it's possible to have a different
        sortLabel per language.
    :rtype: A :class:`Label` or `None` if no label could be found.
    '''
    if not labels:
        return None
    if isinstance(language, str):
        language = [language]
    if not language:
        language = ['und']
    labels = [dict_to_label(l) for l in labels]
    l = False
    for lang in language:
        if sortLabel:
            l = find_best_label_for_type(labels, lang, 'sortLabel')
        if not l:
            l = find_best_label_for_type(labels, lang, 'prefLabel')
        if not l:
            l = find_best_label_for_type(labels, lang, 'altLabel')
        if l:
            return l
    return label(labels, 'any', sortLabel) if 'any' not in language else None


def find_best_label_for_type(labels, language, labeltype):
    '''
    Find the best label for a certain labeltype.

    :param list labels: A list of :class:`Label`.
    :param str language: An IANA language string, eg. `nl` or `nl-BE`.
    :param str labeltype: Type of label to look for, eg. `prefLabel`.
    '''
    typelabels = [l for l in labels if l.type == labeltype]
    if not typelabels:
        return False
    if language == 'any':
        return typelabels[0]
    exact = filter_labels_by_language(typelabels, language)
    if exact:
        return exact[0]
    inexact = filter_labels_by_language(typelabels, language, True)
    if inexact:
        return inexact[0]
    return False


def filter_labels_by_language(labels, language, broader=False):
    '''
    Filter a list of labels, leaving only labels of a certain language.

    :param list labels: A list of :class:`Label`.
    :param str language: An IANA language string, eg. `nl` or `nl-BE`.
    :param boolean broader: When true, will also match `nl-BE` when filtering
        on `nl`. When false, only exact matches are considered.
    '''
    if language == 'any':
        return labels
    if broader:
        language = tags.tag(language).language.format
        return [l for l in labels if tags.tag(l.language).language.format == language]
    else:
        language = tags.tag(language).format
        return [l for l in labels if tags.tag(l.language).format == language]


def dict_to_label(dict):
    '''
    Transform a dict with keys `label`, `type` and `language` into a
    :class:`Label`.

    Only the `label` key is mandatory. If `type` is not present, it will
    default to `prefLabel`. If `language` is not present, it will default
    to `und`.

    If the argument passed is not a dict, this method just
    returns the argument.
    '''
    try:
        return Label(
            dict['label'],
            dict.get('type', 'prefLabel'),
            dict.get('language', 'und')
        )
    except (KeyError, AttributeError, TypeError):
        return dict


def dict_to_note(dict):
    '''
    Transform a dict with keys `note`, `type` and `language` into a
    :class:`Note`.

    Only the `note` key is mandatory. If `type` is not present, it will
    default to `note`. If `language` is not present, it will default to `und`.
    If `markup` is not present it will default to `None`.

    If the argument passed is already a :class:`Note`, this method just returns
    the argument.
    '''
    if isinstance(dict, Note):
        return dict
    return Note(
        dict['note'],
        dict.get('type', 'note'),
        dict.get('language', 'und'),
        dict.get('markup')
    )


def dict_to_source(dict):
    '''
    Transform a dict with key 'citation' into a :class:`Source`.

    If the argument passed is already a :class:`Source`, this method just
    returns the argument.
    '''

    if isinstance(dict, Source):
        return dict
    return Source(
        dict['citation'],
        dict.get('markup')
    )
