"""
This module contains a read-only model of the :term:`SKOS` specification.

To complement the :term:`SKOS` specification, some elements were borrowed
from the :term:`SKOS-THES` specification (eg. superordinate and
subordinate array).

.. versionadded:: 0.2.0
"""

from collections.abc import Sequence
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Literal
from typing import TypeAlias
from typing import TypeVar

from language_tags import tags

from .uri import is_uri

ExtraData = TypeVar("ExtraData")

valid_markup: list[str | None] = [None, "HTML"]
"""
Valid types of markup for a note or a source.
"""


class Label(Generic[ExtraData]):
    """
    A :term:`SKOS` Label.
    """

    uri: str | None
    """A :term:`URI` for this label."""

    label: str
    """
    The label itself (eg. `churches`, `trees`, `Spitfires`, ...)
    """

    type: str
    """
    The type of this label (`prefLabel`, `altLabel`, `hiddenLabel`, 'sortLabel').
    """

    label_types: list[str]
    """
    Zero or more extra types for this label.
    These types should be URI's that map to SKOS Concepts,
    adding some typing but nor formal semantics.
    """

    language: str
    """
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    """

    extra_data: ExtraData | None
    """Extra data attached to this label."""

    valid_types: ClassVar[list[str]] = [
        "prefLabel",
        "altLabel",
        "hiddenLabel",
        "sortLabel",
    ]
    """
    The valid types for a label
    """

    def __init__(
        self,
        label: str,
        type: str = "prefLabel",
        language: str = "und",
        uri: str | None = None,
        label_types: list[str] | None = None,
        extra_data: ExtraData | None = None,
    ) -> None:
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
        self.extra_data = extra_data

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Label):
            return False
        if self.uri:
            return self.uri == other.uri
        return (
            self.label == other.label
            and self.type == other.type
            and self.language == other.language
        )

    def __ne__(self, other: object) -> bool:
        return not self == other

    @staticmethod
    def is_valid_type(type: str) -> bool:
        """
        Check if the argument is a valid SKOS label type.

        :param string type: The type to be checked.
        """
        return type in Label.valid_types

    def is_xl(self) -> bool:
        return self.uri is not None

    def __repr__(self) -> str:
        if not self.is_xl():
            return f"Label('{self.label}', '{self.type}', '{self.language}')"
        return f"Label('{self.label}', '{self.type}', '{self.language}', '{self.uri}')"


class Note(Generic[ExtraData]):
    """
    A :term:`SKOS` Note.
    """

    note: str
    """The note itself"""

    type: str
    """
    The type of this note ( `note`, `definition`, `scopeNote`, ...).
    """

    language: str
    """
    The language the label is in (eg. `en`, `en-US`, `nl`, `nl-BE`).
    """

    markup: str | None
    """
    What kind of markup does the note contain?

    If not `None`, the note should be treated as a certain type of markup.
    Currently only HTML is allowed.
    """

    extra_data: ExtraData | None
    """Extra data attached to this note."""

    valid_types: ClassVar[list[str]] = [
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

    def __init__(
        self,
        note: str,
        type: str = "note",
        language: str = "und",
        markup: str | None = None,
        extra_data: ExtraData | None = None,
    ) -> None:
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
        self.extra_data = extra_data

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return False
        return (
            self.note == other.note
            and self.type == other.type
            and self.language == other.language
        )

    def __ne__(self, other: object) -> bool:
        return not self == other

    @staticmethod
    def is_valid_type(type: str) -> bool:
        """
        Check if the argument is a valid SKOS note type.

        :param string type: The type to be checked.
        """
        return type in Note.valid_types

    @staticmethod
    def is_valid_markup(markup: str | None) -> bool:
        """
        Check the argument is a valid type of markup.

        :param string markup: The type to be checked.
        """
        return markup in valid_markup


class Source(Generic[ExtraData]):
    """
    A `Source` for a concept, collection or scheme.

    """

    citation: str
    """A bibliographic citation for this source."""

    markup: str | None
    """
    What kind of markup does the source contain?

    If not `None`, the source should be treated as a certain type of markup.
    Currently only HTML is allowed.
    """

    extra_data: ExtraData | None
    """Extra data attached to this source."""

    def __init__(
        self,
        citation: str,
        markup: str | None = None,
        extra_data: ExtraData | None = None,
    ) -> None:
        self.citation = citation
        if self.is_valid_markup(markup):
            self.markup = markup
        else:
            raise ValueError(f"{markup} is not valid markup.")
        self.extra_data = extra_data

    @staticmethod
    def is_valid_markup(markup: str | None) -> bool:
        """
        Check the argument is a valid type of markup.

        :param string markup: The type to be checked.
        """
        return markup in valid_markup


class ConceptScheme(Generic[ExtraData]):
    """
    A :term:`SKOS` ConceptScheme.

    :param string uri: A :term:`URI` for this conceptscheme.
    :param list labels: A list of :class:`skosprovider.skos.Label` instances.
    :param list notes: A list of :class:`skosprovider.skos.Note` instances.
    """

    uri: str
    """A :term:`URI` for this conceptscheme."""

    labels: list[Label]
    """A :class:`lst` of :class:`skosprovider.skos.label` instances."""

    notes: list[Note]
    """A :class:`lst` of :class:`skosprovider.skos.Note` instances."""

    sources: list[Source]
    """A :class:`lst` of :class:`skosprovider.skos.Source` instances."""

    languages: list[str]
    """
    A :class:`lst` of languages that are being used in the ConceptScheme.

    There's no guarantuee that labels or notes in other languages do not exist.
    """

    extra_data: ExtraData | None
    """Extra data attached to this concept scheme."""

    def __init__(
        self,
        uri: str,
        labels: list[Label | dict] | None = None,
        notes: list[Note | dict] | None = None,
        sources: list[Source | dict] | None = None,
        languages: list[str] | None = None,
        extra_data: ExtraData | None = None,
    ) -> None:
        if not is_uri(uri):
            raise ValueError(f"{uri} is not a valid URI.")
        self.uri = uri
        self.labels = [dict_to_label(lbl) for lbl in labels] if labels else []
        self.notes = [dict_to_note(note) for note in notes] if notes else []
        self.sources = [dict_to_source(source) for source in sources] if sources else []
        self.languages = languages or []
        self.extra_data = extra_data

    def label(self, language: str | list[str] = "any") -> Label | None:
        """
        Provide a single label for this conceptscheme.

        This uses the :func:`label` function to determine which label to
        return.

        :param string language: The preferred language to receive the label in.
            This should be a valid IANA language tag.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        """
        return label(self.labels, language)

    def _sortkey(self, key: str = "uri", language: str | list[str] = "any") -> str:
        """
        Provide a single sortkey for this conceptscheme.

        :param string key: Either `uri`, `label` or `sortlabel`.
        :param string language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
        :rtype: :class:`str`
        """
        if key == "uri":
            return self.uri
        else:
            sortlabel = label(self.labels, language, key == "sortlabel")
            return sortlabel.label.lower() if sortlabel else ""

    def __repr__(self) -> str:
        return f"ConceptScheme('{self.uri}')"


class Concept(Generic[ExtraData]):
    """
    A :term:`SKOS` Concept.
    """

    id: Any
    """An id for this Concept within a vocabulary

    eg. 12345
    """

    uri: str | None
    """A proper uri for this Concept

    eg. `http://id.example.com/skos/trees/1`
    """

    type: Literal["concept"]
    """The type of this concept or collection.

    eg. 'concept'
    """

    concept_scheme: ConceptScheme | None
    """The :class:`ConceptScheme` this Concept is a part of."""

    labels: list[Label]
    """A :class:`lst` of :class:`Label` instances."""

    notes: list[Note]
    """A :class:`lst` of :class:`Note` instances."""

    sources: list[Source]
    """A :class:`lst` of :class:`skosprovider.skos.Source` instances."""

    broader: list[Any]
    """A :class:`lst` of concept ids."""

    narrower: list[Any]
    """A :class:`lst` of concept ids."""

    related: list[Any]
    """A :class:`lst` of concept ids."""

    member_of: list[Any]
    """A :class:`lst` of collection ids."""

    subordinate_arrays: list[Any]
    """A :class:`list` of collection ids."""

    matches: dict[str, list[str]]
    """
    A :class:`dictionary`. Each key is a matchtype and
    contains a :class:`list` of URI's.
    """

    extra_data: ExtraData | None
    """Extra data attached to this concept."""

    matchtypes: ClassVar[list[str]] = ["close", "exact", "related", "broad", "narrow"]
    """Matches with Concepts in other ConceptSchemes.

    This dictionary contains a key for each type of Match (close, exact,
    related, broad, narrow). Attached to each key is a list of URI's.
    """

    def __init__(
        self,
        id: Any,
        uri: str | None = None,
        concept_scheme: ConceptScheme | None = None,
        labels: list[Label | dict] | None = None,
        notes: list[Note | dict] | None = None,
        sources: list[Source | dict] | None = None,
        broader: list[Any] | None = None,
        narrower: list[Any] | None = None,
        related: list[Any] | None = None,
        member_of: list[Any] | None = None,
        subordinate_arrays: list[Any] | None = None,
        matches: dict[str, list[str]] | None = None,
        extra_data: ExtraData | None = None,
    ) -> None:
        self.id = id
        self.uri = uri
        self.type = "concept"
        self.concept_scheme = concept_scheme
        self.labels = [dict_to_label(lbl) for lbl in labels] if labels else []
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
        self.extra_data = extra_data

    def label(self, language: str | list[str] = "any") -> Label | None:
        """
        Provide a single label for this concept.

        This uses the :func:`label` function to determine which label to return.

        :param string language: The preferred language to receive the label in.
            This should be a valid IANA language tag or a list of language tags.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        """
        return label(self.labels, language)

    def _sortkey(self, key: str = "id", language: str | list[str] = "any") -> str:
        """
        Provide a single sortkey for this concept.

        :param string key: Either `id`, `uri`, `label` or `sortlabel`.
        :param string language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
        :rtype: :class:`str`
        """
        if key == "id":
            return str(self.id)
        elif key == "uri":
            return self.uri if self.uri else ""
        else:
            sortlabel = label(self.labels, language, key == "sortlabel")
            return sortlabel.label.lower() if sortlabel else ""

    def __repr__(self) -> str:
        return f"Concept('{self.id}')"


class Collection(Generic[ExtraData]):
    """
    A :term:`SKOS` Collection.
    """

    id: Any
    """An id for this Collection within a vocabulary"""

    uri: str | None
    """A proper uri for this Collection"""

    type: Literal["collection"]
    """The type of this concept or collection.

    eg. 'collection'
    """

    concept_scheme: ConceptScheme | None
    """The :class:`ConceptScheme` this Collection is a part of."""

    labels: list[Label]
    """A :class:`lst` of :class:`skosprovider.skos.label` instances."""

    notes: list[Note]
    """A :class:`lst` of :class:`skosprovider.skos.Note` instances."""

    sources: list[Source]
    """A :class:`lst` of :class:`skosprovider.skos.Source` instances."""

    members: list[Any]
    """A :class:`lst` of concept or collection ids."""

    member_of: list[Any]
    """A :class:`lst` of collection ids."""

    superordinates: list[Any]
    """A :class:`lst` of concept ids."""

    infer_concept_relations: bool
    """Should member concepts of this collection be seen as narrower concept of
    a superordinate of the collection?"""

    extra_data: ExtraData | None
    """Extra data attached to this collection."""

    def __init__(
        self,
        id: Any,
        uri: str | None = None,
        concept_scheme: ConceptScheme | None = None,
        labels: list[Label | dict] | None = None,
        notes: list[Note | dict] | None = None,
        sources: list[Source | dict] | None = None,
        members: list[Any] | None = None,
        member_of: list[Any] | None = None,
        superordinates: list[Any] | None = None,
        infer_concept_relations: bool = True,
        extra_data: ExtraData | None = None,
    ) -> None:
        self.id = id
        self.uri = uri
        self.type = "collection"
        self.concept_scheme = concept_scheme
        self.labels = [dict_to_label(lbl) for lbl in labels] if labels else []
        self.notes = [dict_to_note(note) for note in notes] if notes else []
        self.sources = [dict_to_source(source) for source in sources] if sources else []
        self.members = members or []
        self.member_of = member_of or []
        self.superordinates = superordinates or []
        self.infer_concept_relations = infer_concept_relations
        self.extra_data = extra_data

    def label(self, language: str | list[str] = "any") -> Label | None:
        """
        Provide a single label for this collection.

        This uses the :func:`label` function to determine which label to return.

        :param string language: The preferred language to receive the label in.
            This should be a valid IANA language tag.
        :rtype: :class:`skosprovider.skos.Label` or None if no labels were found.
        """
        return label(self.labels, language)

    def _sortkey(self, key: str = "id", language: str | list[str] = "any") -> str:
        """
        Provide a single sortkey for this collection.

        :param string key: Either `id`, `uri`, `label` or `sortlabel`.
        :param string language: The preferred language to receive the label in
            if key is `label` or `sortlabel`. This should be a valid IANA language tag.
        :rtype: :class:`str`
        """
        if key == "id":
            return str(self.id)
        elif key == "uri":
            return self.uri if self.uri else ""
        else:
            sortlabel = label(self.labels, language, key == "sortlabel")
            return sortlabel.label.lower() if sortlabel else ""

    def __repr__(self) -> str:
        return f"Collection('{self.id}')"


def label(
    labels: Sequence[Label | dict] | None = None,
    language: str | list[str] | None = "any",
    sortLabel: bool = False,
) -> Label | None:
    """
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
    """
    if not labels:
        return None
    if isinstance(language, str):
        langs: list[str] = [language]
    elif isinstance(language, list):
        langs = language
    else:
        langs = ["und"]
    langs = [lang for lang in langs if tags.tag(lang).language] or ["und"]
    actual_labels = [dict_to_label(lbl_or_dict) for lbl_or_dict in labels]
    return_label: Label | Literal[False] = False
    for lang in langs:
        if sortLabel:
            return_label = find_best_label_for_type(actual_labels, lang, "sortLabel")
        if not return_label:
            return_label = find_best_label_for_type(actual_labels, lang, "prefLabel")
        if not return_label:
            return_label = find_best_label_for_type(actual_labels, lang, "altLabel")
        if return_label:
            return return_label
    return label(labels, "any", sortLabel) if "any" not in langs else None


def find_best_label_for_type(
    labels: Sequence[Label],
    language: str,
    labeltype: str,
) -> Label | Literal[False]:
    """
    Find the best label for a certain labeltype.

    :param list labels: A list of :class:`Label`.
    :param str language: An IANA language string, eg. `nl` or `nl-BE`.
    :param str labeltype: Type of label to look for, eg. `prefLabel`.
    """
    typelabels = [lbl for lbl in labels if lbl.type == labeltype]
    if not typelabels:
        return False
    if language == "any":
        return typelabels[0]
    exact = filter_labels_by_language(typelabels, language)
    if exact:
        return exact[0]
    inexact = filter_labels_by_language(typelabels, language, True)
    if inexact:
        return inexact[0]
    return False


def filter_labels_by_language(
    labels: Sequence[Label],
    language: str,
    broader: bool = False,
) -> Sequence[Label]:
    """
    Filter a list of labels, leaving only labels of a certain language.

    :param list labels: A list of :class:`Label`.
    :param str language: An IANA language string, eg. `nl` or `nl-BE`.
    :param boolean broader: When true, will also match `nl-BE` when filtering
        on `nl`. When false, only exact matches are considered.
    """
    if language == "any":
        return labels
    if broader:
        lang_subtag = tags.tag(language).language
        if lang_subtag is None:
            return []
        language = lang_subtag.format
        return [
            lbl
            for lbl in labels
            if (subtag := tags.tag(lbl.language).language) is not None
            and subtag.format == language
        ]
    else:
        language = tags.tag(language).format
        return [
            lbl for lbl in labels if tags.tag(lbl.language).format == language
        ]


def dict_to_label(value: Label | dict) -> Label[dict]:
    """
    Transform a dict with keys `label`, `type`, `language` and `uri`
    into a :class:`Label`.

    Only the `label` key is mandatory. If `type` is not present, it will
    default to `prefLabel`. If `language` is not present, it will default
    to `und`.

    If the argument passed is not a dict, this method just
    returns the argument.
    """
    if isinstance(value, Label):
        return value
    value = value.copy()
    return Label(
        value.pop("label"),
        value.pop("type", "prefLabel"),
        value.pop("language", "und"),
        uri=value.pop("uri", None),
        label_types=value.pop("label_types", []),
        extra_data=value,
    )


def dict_to_note(value: Note | dict) -> Note[dict]:
    """
    Transform a dict with keys `note`, `type` and `language` into a
    :class:`Note`.

    Only the `note` key is mandatory. If `type` is not present, it will
    default to `note`. If `language` is not present, it will default to `und`.
    If `markup` is not present it will default to `None`.

    If the argument passed is already a :class:`Note`, this method just returns
    the argument.
    """
    if isinstance(value, Note):
        return value
    value = value.copy()
    return Note(
        value.pop("note"),
        value.pop("type", "note"),
        value.pop("language", "und"),
        value.pop("markup", None),
        extra_data=value,
    )


def dict_to_source(value: Source | dict) -> Source[dict]:
    """
    Transform a dict with key 'citation' into a :class:`Source`.

    If the argument passed is already a :class:`Source`, this method just
    returns the argument.
    """
    if isinstance(value, Source):
        return value
    value = value.copy()
    return Source(
        value.pop("citation"),
        value.pop("markup", None),
        extra_data=value,
    )


SkosObject: TypeAlias = Concept | Collection | ConceptScheme | Label | Note | Source
