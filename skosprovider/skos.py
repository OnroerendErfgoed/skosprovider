"""
This module contains a read-only model of the :term:`SKOS` specification.

To complement the :term:`SKOS` specification, some elements were borrowed
from the :term:`SKOS-THES` specification (eg. superordinate and
subordinate array).

.. versionadded:: 0.2.0
"""

from language_tags import tags

from .uri import is_uri

valid_markup = [None, "HTML"]
"""
Valid types of markup for a note or a source.
"""


class Label:
    """
    A :term:`SKOS` Label.
    """

    uri = None
    """A :term:`URI` for this label."""

    label = None
    """
    The label itself (eg. `churches`, `trees`, `Spitfires`, ...)
    """

    type = "prefLabel"
    """
    The type of this label (`prefLabel`, `altLabel`, `hiddenLabel`, 'sortLabel').
    """

    label_types = []
    """
    Zero or more extra types for this label.
    These types should be URI's that map to SKOS Concepts,
    adding some typing but nor formal semantics.
    """

    language = "und"
    """
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    """

    valid_types = ["prefLabel", "altLabel", "hiddenLabel", "sortLabel"]
    """
    The valid types for a label
    """

    def __init__(
        self, label, type="prefLabel", language="und", uri=None, label_types=None
    ):
        self.label = label
        self.type = type
        if not language:
            language = "und"
        if tags.check(language):
            self.language = language
        else:
            raise ValueError(f"{language} is not a valid IANA language tag.")
        if uri and not is_uri(uri):
            raise ValueError(f"{uri} is not a valid URI.")
        self.uri = uri
        if self.is_xl() and label_types:
            self.label_types = label_types
        else:
            self.label_types = []

    def __eq__(self, other):
        if not isinstance(other, Label):
            return False
        if self.uri:
            return self.uri == other.uri
        return (
            self.label == other.label
            and self.type == other.type
            and self.language == other.language
        )

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def is_valid_type(type):
        """
        Check if the argument is a valid SKOS label type.

        :param string type: The type to be checked.
        """
        return type in Label.valid_types

    def is_xl(self):
        return self.uri is not None

    def __repr__(self):
        if not self.is_xl():
            return f"Label('{self.label}', '{self.type}', '{self.language}')"
        return f"Label('{self.label}', '{self.type}', '{self.language}', '{self.uri}')"


class Note:
    """
    A :term:`SKOS` Note.
    """

    note = None
    """The note itself"""

    type = "note"
    """
    The type of this note ( `note`, `definition`, `scopeNote`, ...).
    """

    language = "und"
    """
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    """

    markup = None
    """
    What kind of markup does the note contain?

    If not `None`, the note should be treated as a certain type of markup.
    Currently only HTML is allowed.
    """

    valid_types = [
        "note",
        "changeNote",
        "definition",
        "editorialNote",
        "example",
        "historyNote",
        "scopeNote",
    ]
    """
    The valid types for a note.
    """

    def __init__(self, note, type="note", language="und", markup=None):
        self.note = note
        self.type = type
        if not language:
            language = "und"
        if tags.check(language):
            self.language = language
        else:
            raise ValueError(f"{language} is not a valid IANA language tag.")
        if self.is_valid_markup(markup):
            self.markup = markup
        else:
            raise ValueError(f"{markup} is not valid markup.")

    def __eq__(self, other):
        if not isinstance(other, Note):
            return False
        return (
            self.note == other.note
            and self.type == other.type
            and self.language == other.language
        )

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def is_valid_type(type):
        """
        Check if the argument is a valid SKOS note type.

        :param string type: The type to be checked.
        """
        return type in Note.valid_types

    @staticmethod
    def is_valid_markup(markup):
        """
        Check the argument is a valid type of markup.

        :param string markup: The type to be checked.
        """
        return markup in valid_markup


class Source:
    """
    A `Source` for a concept, collection or scheme.

    """

    citation = None
    """A bibliographic citation for this source."""

    markup = None
    """
    What kind of markup does the source contain?

    If not `None`, the source should be treated as a certain type of markup.
    Currently only HTML is allowed.
    """

    def __init__(self, citation, markup=None):
        self.citation = citation
        if self.is_valid_markup(markup):
            self.markup = markup
        else:
            raise ValueError(f"{markup} is not valid markup.")

    @staticmethod
    def is_valid_markup(markup):
        """
        Check the argument is a valid type of markup.

        :param string markup: The type to be checked.
        """
        return markup in valid_markup


class ConceptScheme:
    """
    A :term:`SKOS` ConceptScheme.

    :param string uri: A :term:`URI` for this conceptscheme.
    :param list labels: A list of :class:`skosprovider.skos.Label` instances.
    :param list notes: A list of :class:`skosprovider.skos.Note` instances.
    """

    uri = None
    """A :term:`URI` for this conceptscheme."""

    labels = []
    """A :class:`lst` of :class:`skosprovider.skos.label` instances."""

    notes = []
    """A :class:`lst` of :class:`skosprovider.skos.Note` instances."""

    sources = []
    """A :class:`lst` of :class:`skosprovider.skos.Source` instances."""

    languages = []
    """
    A :class:`lst` of languages that are being used in the ConceptScheme.

    There's no guarantuee that labels or notes in other languages do not exist.
    """

    def __init__(
        self,
        uri,
        labels=None,
        notes=None,
        sources=None,
        languages=None,
        default_language=None,
    ):
        if not is_uri(uri):
            raise ValueError(f"{uri} is not a valid URI.")
        self.uri = uri
        self.labels = [dict_to_label(label) for label in labels] if labels else []
        self.notes = [dict_to_note(note) for note in notes] if notes else []
        self.sources = [dict_to_source(source) for source in sources] if sources else []
        self.languages = languages or []
        self.default_language = default_language

    def label(self, language=None):
        """
        Provide a single label for this conceptscheme.

        This uses the :func:`label` function to determine which label to
        return.

        :param string language: The preferred language to receive the label in.
            This should be a valid IANA language tag. If not specified or `None`,
            the :attr:`default_language` will be used, falling back to any
            available label.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        """
        return label(self.labels, self._resolve_language(language))

    def _sortkey(self, key="uri", language=None):
        """
        Provide a single sortkey for this conceptscheme.

        :param string key: Either `uri`, `label` or `sortlabel`.
        :param string language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
            If not specified or `None`, the :attr:`default_language` will be used.
        :rtype: :class:`str`
        """
        if key == "uri":
            return self.uri
        sortlabel = label(
            self.labels, self._resolve_language(language), key == "sortlabel"
        )
        return sortlabel.label.lower() if sortlabel else ""

    def _resolve_language(self, language):
        return _resolve_language(language, self.default_language)

    def __repr__(self):
        return f"ConceptScheme('{self.uri}')"


class Concept:
    """
    A :term:`SKOS` Concept.
    """

    id = None
    """An id for this Concept within a vocabulary

    eg. 12345
    """

    uri = None
    """A proper uri for this Concept

    eg. `http://id.example.com/skos/trees/1`
    """

    type = "concept"
    """The type of this concept or collection.

    eg. 'concept'
    """

    concept_scheme = None
    """The :class:`ConceptScheme` this Concept is a part of."""

    labels = []
    """A :class:`lst` of :class:`Label` instances."""

    notes = []
    """A :class:`lst` of :class:`Note` instances."""

    sources = []
    """A :class:`lst` of :class:`skosprovider.skos.Source` instances."""

    broader = []
    """A :class:`lst` of concept ids."""

    narrower = []
    """A :class:`lst` of concept ids."""

    related = []
    """A :class:`lst` of concept ids."""

    member_of = []
    """A :class:`lst` of collection ids."""

    subordinate_arrays = []
    """A :class:`list` of collection ids."""

    matches = ({},)
    """
    A :class:`dictionary`. Each key is a matchtype and
    contains a :class:`list` of URI's.
    """

    matchtypes = ["close", "exact", "related", "broad", "narrow"]
    """Matches with Concepts in other ConceptSchemes.

    This dictionary contains a key for each type of Match (close, exact,
    related, broad, narrow). Attached to each key is a list of URI's.
    """

    def __init__(
        self,
        id,
        uri=None,
        concept_scheme=None,
        labels=None,
        notes=None,
        sources=None,
        broader=None,
        narrower=None,
        related=None,
        member_of=None,
        subordinate_arrays=None,
        matches=None,
        default_language=None,
    ):
        self.id = id
        self.uri = uri
        self.type = "concept"
        self.concept_scheme = concept_scheme
        self.labels = [dict_to_label(label) for label in labels] if labels else []
        self.notes = [dict_to_note(note) for note in notes] if notes else []
        self.sources = [dict_to_source(source) for source in sources] if sources else []
        self.broader = broader or []
        self.narrower = narrower or []
        self.related = related or []
        self.member_of = member_of or []
        self.subordinate_arrays = subordinate_arrays or []
        self.matches = {key: [] for key in self.matchtypes}
        if matches:
            self.matches.update(matches)
        self.default_language = default_language

    def label(self, language=None):
        """
        Provide a single label for this concept.

        This uses the :func:`label` function to determine which label to return.

        :param language: The preferred language to receive the label in.
            This should be a valid IANA language tag or a list of language tags.
            If not specified or `None`, the :attr:`default_language` will be used,
            falling back to any available label.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        """
        return label(self.labels, self._resolve_language(language))

    def _sortkey(self, key="id", language=None):
        """
        Provide a single sortkey for this collection.

        :param string key: Either `id`, `uri`, `label` or `sortlabel`.
        :param language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
            If not specified or `None`, the :attr:`default_language` will be used.
        :rtype: :class:`str`
        """
        if key == "id":
            return str(self.id)
        elif key == "uri":
            return self.uri if self.uri else ""
        sortlabel = label(
            self.labels, self._resolve_language(language), key == "sortlabel"
        )
        return sortlabel.label.lower() if sortlabel else ""

    def _resolve_language(self, language):
        return _resolve_language(language, self.default_language)

    def __repr__(self):
        return f"Concept('{self.id}')"


class Collection:
    """
    A :term:`SKOS` Collection.
    """

    id = None
    """An id for this Collection within a vocabulary"""

    uri = None
    """A proper uri for this Collection"""

    type = "collection"
    """The type of this concept or collection.

    eg. 'collection'
    """

    concept_scheme = None
    """The :class:`ConceptScheme` this Collection is a part of."""

    labels = []
    """A :class:`lst` of :class:`skosprovider.skos.label` instances."""

    notes = []
    """A :class:`lst` of :class:`skosprovider.skos.Note` instances."""

    sources = []
    """A :class:`lst` of :class:`skosprovider.skos.Source` instances."""

    members = []
    """A :class:`lst` of concept or collection ids."""

    member_of = []
    """A :class:`lst` of collection ids."""

    superordinates = []
    """A :class:`lst` of concept ids."""

    infer_concept_relations = True
    """Should member concepts of this collection be seen as narrower concept of
    a superordinate of the collection?"""

    def __init__(
        self,
        id,
        uri=None,
        concept_scheme=None,
        labels=None,
        notes=None,
        sources=None,
        members=None,
        member_of=None,
        superordinates=None,
        infer_concept_relations=True,
        default_language=None,
    ):
        self.id = id
        self.uri = uri
        self.type = "collection"
        self.concept_scheme = concept_scheme
        self.labels = [dict_to_label(label) for label in labels] if labels else []
        self.notes = [dict_to_note(note) for note in notes] if notes else []
        self.sources = [dict_to_source(source) for source in sources] if sources else []
        self.members = members or []
        self.member_of = member_of or []
        self.superordinates = superordinates or []
        self.infer_concept_relations = infer_concept_relations
        self.default_language = default_language

    def label(self, language=None):
        """
        Provide a single label for this collection.

        This uses the :func:`label` function to determine which label to return.

        :param language: The preferred language to receive the label in.
            This should be a valid IANA language tag. If not specified or `None`,
            the :attr:`default_language` will be used, falling back to any
            available label.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        """
        return label(self.labels, self._resolve_language(language), False)

    def _sortkey(self, key="id", language=None):
        """
        Provide a single sortkey for this collection.

        :param string key: Either `id`, `uri`, `label` or `sortlabel`.
        :param language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
            If not specified or `None`, the :attr:`default_language` will be used.
        :rtype: :class:`str`
        """
        if key == "id":
            return str(self.id)
        elif key == "uri":
            return self.uri if self.uri else ""
        sortlabel = label(
            self.labels, self._resolve_language(language), key == "sortlabel"
        )
        return sortlabel.label.lower() if sortlabel else ""

    def _resolve_language(self, language):
        return _resolve_language(language, self.default_language)

    def __repr__(self):
        return f"Collection('{self.id}')"


def _resolve_language(language, default_language):
    """Combine an explicit language with the configured default."""
    if language is None:
        return default_language
    if isinstance(language, str):
        language = [language]
    else:
        language = list(language)
    if default_language and default_language not in language:
        language.append(default_language)
    return language


def label(labels=None, language=None, sortLabel=False):
    """
    Provide a label for a list of labels.

    The items in the list of labels are assumed to be either instances of
    :class:`Label`, or dicts with at least the key `label` in them. These will
    be passed to the :func:`dict_to_label` function.

    Within each candidate language the function prefers a `prefLabel` over an
    `altLabel` (and a `sortLabel` over both when `sortLabel=True`). Hidden
    labels are never considered.

    Language resolution:

    - Passing `None` (or omitting the argument) means "no preference" --
      any available label is returned.
    - Passing a specific IANA language tag such as `en-GB` will first look for
      an exact match on that tag, then progressively drop subtags
      (e.g. `nl-BE-Latn` -> `nl-BE` -> `nl`). The literal tag `und` behaves
      like any other tag and only matches labels explicitly tagged as `und`.
    - Passing a list of tags tries each in turn, applying the same subtag
      fallback to each.
    - If no language-specific label can be found, the function falls back to
      returning any available label, regardless of language. If the list of
      labels is empty (or only contains hidden labels), `None` is returned.

    .. versionchanged:: 2.0.0
        The magic value `"any"` is no longer supported -- pass `None` instead.
        `None` no longer means "labels explicitly tagged as `und`"; use the
        tag `"und"` for that. Language matching now walks down the subtag
        chain rather than collapsing straight to the primary language.

    .. versionchanged:: 1.1
        It is now possible to pass a list of languages.

    :param labels: A list of :class:`Label` (or dicts convertible to one).
    :param language: The preferred language to receive the label in. This
        should be a valid IANA language tag, a list of such tags, or `None`.
    :param boolean sortLabel: Should sortLabels be considered or not? If True,
        sortLabels will be preferred over prefLabels. Bear in mind that these
        are still language dependent. So, it's possible to have a different
        sortLabel per language.
    :rtype: A :class:`Label` or `None` if no label could be found.
    """
    if not labels:
        return None
    labels = [dict_to_label(label) for label in labels]

    if language is None:
        return _pick_best_label(labels, sortLabel)

    if isinstance(language, str):
        language = [language]
    language = [lang for lang in language if lang and tags.tag(lang).language]

    type_order = ("prefLabel", "altLabel")
    if sortLabel:
        type_order = ("sortLabel",) + type_order

    for lang in language:
        for labeltype in type_order:
            found = find_best_label_for_type(labels, lang, labeltype)
            if found:
                return found

    return _pick_best_label(labels, sortLabel)


def _language_fallback_chain(language):
    """Yield progressively less specific forms of an IANA language tag.

    For `nl-BE-Latn` this yields `nl-BE-Latn`, `nl-BE`, `nl`.
    """
    parts = language.split("-")
    while parts:
        yield "-".join(parts)
        parts.pop()


def _primary_language(language):
    """Return the canonical primary subtag of an IANA language tag, or None."""
    subtag = tags.tag(language).language
    return subtag.format if subtag else None


def _pick_best_label(labels, sortLabel):
    """Pick the best-typed label from a list, disregarding language."""
    if not labels:
        return None
    type_order = ("prefLabel", "altLabel")
    if sortLabel:
        type_order = ("sortLabel",) + type_order
    for ltype in type_order:
        for lbl in labels:
            if lbl.type == ltype:
                return lbl
    return None


def find_best_label_for_type(labels, language, labeltype):
    """
    Find the best label of a specific type in a given language.

    First tries an exact match on the language tag, then walks down the
    subtag chain (e.g. `nl-BE-Latn` -> `nl-BE` -> `nl`). If still nothing
    matches, falls back to any label that shares the same primary language
    subtag (so `en-GB` will also match `en-US` once the more specific tries
    are exhausted). Returns `False` if nothing matches.

    :param list labels: A list of :class:`Label`.
    :param str language: An IANA language string, eg. `nl` or `nl-BE`.
    :param str labeltype: Type of label to look for, eg. `prefLabel`.
    """
    typelabels = [lbl for lbl in labels if lbl.type == labeltype]
    if not typelabels:
        return False
    for candidate in _language_fallback_chain(language):
        matches = filter_labels_by_language(typelabels, candidate)
        if matches:
            return matches[0]
    primary = _primary_language(language)
    if primary:
        family = [
            lbl for lbl in typelabels if _primary_language(lbl.language) == primary
        ]
        if family:
            return family[0]
    return False


def filter_labels_by_language(labels, language):
    """
    Filter a list of labels, leaving only labels of a certain language.

    Matches the IANA language tag exactly (canonicalised via
    :mod:`language_tags`). To walk the subtag chain, iterate with
    :func:`_language_fallback_chain` yourself.

    .. versionchanged:: 2.0.0
        The `broader` parameter and the magic `"any"` value have been removed.

    :param list labels: A list of :class:`Label`.
    :param str language: An IANA language string, eg. `nl` or `nl-BE`.
    """
    target = tags.tag(language).format
    return [lbl for lbl in labels if tags.tag(lbl.language).format == target]


def dict_to_label(dict):
    """
    Transform a dict with keys `label`, `type`, `language` and `uri`
    into a :class:`Label`.

    Only the `label` key is mandatory. If `type` is not present, it will
    default to `prefLabel`. If `language` is not present, it will default
    to `und`.

    If the argument passed is not a dict, this method just
    returns the argument.
    """
    try:
        return Label(
            dict["label"],
            dict.get("type", "prefLabel"),
            dict.get("language", "und"),
            uri=dict.get("uri"),
            label_types=dict.get("label_types", []),
        )
    except (KeyError, AttributeError, TypeError):
        return dict


def dict_to_note(dict):
    """
    Transform a dict with keys `note`, `type` and `language` into a
    :class:`Note`.

    Only the `note` key is mandatory. If `type` is not present, it will
    default to `note`. If `language` is not present, it will default to `und`.
    If `markup` is not present it will default to `None`.

    If the argument passed is already a :class:`Note`, this method just returns
    the argument.
    """
    if isinstance(dict, Note):
        return dict
    return Note(
        dict["note"],
        dict.get("type", "note"),
        dict.get("language", "und"),
        dict.get("markup"),
    )


def dict_to_source(dict):
    """
    Transform a dict with key 'citation' into a :class:`Source`.

    If the argument passed is already a :class:`Source`, this method just
    returns the argument.
    """

    if isinstance(dict, Source):
        return dict
    return Source(dict["citation"], dict.get("markup"))
