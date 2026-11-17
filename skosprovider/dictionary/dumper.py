"""
This module dumps skos providers to a list of dicts.
"""

from typing import Any

from skosprovider.dictionary.extra_data import ExtraDataDumper
from skosprovider.dictionary.extra_data import dump_extra_data
from skosprovider.extra_data import exception_context
from skosprovider.extra_data import ignore
from skosprovider.provider import VocabularyProvider
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source


def dict_dumper(
    provider: VocabularyProvider, extra_data_dumper: ExtraDataDumper = ignore
) -> list[dict[str, Any]]:
    """
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.dictionary.provider.DictionaryProvider`.

    :param skosprovider.provider.VocabularyProvider provider: The provider
        that wil be turned into a `dict`.
    :param extra_data_dumper: A callable that receives a concept, collection,
        label, note or source and returns a dict or `None`. The dict is merged
        into the dump of that object and overwrites keys that already exist.
        See :mod:`skosprovider.dictionary.extra_data` for the available
        dumpers. Defaults to :func:`~skosprovider.extra_data.ignore`.
    :rtype: A list of dicts.

    .. versionadded:: 0.2.0
    """
    ret = []
    for stuff in provider.get_all():
        concept_or_collection = provider.get_by_id(stuff["id"])
        with exception_context(
            f"{concept_or_collection.type} {concept_or_collection.id!r}"
        ):
            labels = []
            for label in concept_or_collection.labels:
                label_dict = {
                    "language": label.language,
                    "type": label.type,
                    "label": label.label,
                }
                if label.uri:
                    label_dict["uri"] = label.uri
                    if len(label.label_types):
                        label_dict["label_types"] = label.label_types
                label_dict.update(_dump_nested(extra_data_dumper, label))
                labels.append(label_dict)
            notes = []
            for note in concept_or_collection.notes:
                note_dict = {
                    "note": note.note,
                    "type": note.type,
                    "language": note.language,
                    "markup": note.markup,
                }
                if note.uri:
                    note_dict["uri"] = note.uri
                note_dict.update(_dump_nested(extra_data_dumper, note))
                notes.append(note_dict)
            sources = []
            for source in concept_or_collection.sources:
                source_dict = {"citation": source.citation, "markup": source.markup}
                if source.uri:
                    source_dict["uri"] = source.uri
                source_dict.update(_dump_nested(extra_data_dumper, source))
                sources.append(source_dict)
            extra = dump_extra_data(extra_data_dumper, concept_or_collection)
        if isinstance(concept_or_collection, Concept):
            ret.append(
                {
                    "id": concept_or_collection.id,
                    "uri": concept_or_collection.uri,
                    "type": concept_or_collection.type,
                    "labels": labels,
                    "notes": notes,
                    "sources": sources,
                    "narrower": concept_or_collection.narrower,
                    "broader": concept_or_collection.broader,
                    "related": concept_or_collection.related,
                    "member_of": concept_or_collection.member_of,
                    "subordinate_arrays": concept_or_collection.subordinate_arrays,
                    "matches": concept_or_collection.matches,
                    **extra,
                }
            )
        elif isinstance(concept_or_collection, Collection):
            ret.append(
                {
                    "id": concept_or_collection.id,
                    "uri": concept_or_collection.uri,
                    "type": concept_or_collection.type,
                    "labels": labels,
                    "notes": notes,
                    "sources": sources,
                    "members": concept_or_collection.members,
                    "member_of": concept_or_collection.member_of,
                    "superordinates": concept_or_collection.superordinates,
                    "infer_concept_relations": concept_or_collection.infer_concept_relations,  # NoQa: B950
                    **extra,
                }
            )
    return ret


def _dump_nested(
    extra_data_dumper: ExtraDataDumper, obj: Label | Note | Source
) -> dict[str, Any]:
    with exception_context(repr(obj)):
        return dump_extra_data(extra_data_dumper, obj)
