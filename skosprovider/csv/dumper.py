"""
This module dumps skos providers to csv rows.
"""

from skosprovider.csv.extra_data import CsvExtraDataDumper
from skosprovider.exceptions import ExtraDataException
from skosprovider.extra_data import exception_context
from skosprovider.extra_data import ignore
from skosprovider.provider import VocabularyProvider
from skosprovider.skos import Concept
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source


def csv_dumper(
    provider: VocabularyProvider,
    *,
    language: str | None = None,
    extra_data_dumper: CsvExtraDataDumper = ignore,
) -> list[list[str]]:
    """
    Dump a provider to rows that can be passed to a
    :class:`skosprovider.csv.provider.SimpleCsvProvider`, eg. after writing
    them with :func:`csv.writer`.

    Every concept becomes a row `<id>,<preflabel>,<note>,<source>`, with the
    best label in `language`, the first note of type `note` and the first
    source. Collections and everything else that does not fit in such a row
    are left out.

    :param provider: The provider to dump.
    :param language: The language of the label. Defaults to the
        `default_language` of the provider, or any language.
    :param extra_data_dumper: A callable that receives the concept, its label,
        note and source and returns a dict of cells by column index, or
        `None`. The cells are merged into the row of the concept, in the order
        concept, label, note, source, and overwrite any cell already there.
        The row is padded with empty cells up to the highest index. See
        :mod:`skosprovider.csv.extra_data` for the available dumpers. Defaults
        to :func:`~skosprovider.extra_data.ignore`.
    :returns: A list of rows, without trailing empty cells.
    """
    if language is None:
        language = provider.metadata.get("default_language", "any")
    rows = []
    for item in provider.get_all():
        concept = provider.get_by_id(item["id"])
        if isinstance(concept, Concept):
            with exception_context(f"concept {concept.id!r}"):
                rows.append(_row(concept, language, extra_data_dumper))
    return rows


def _row(
    concept: Concept, language: str, extra_data_dumper: CsvExtraDataDumper
) -> list[str]:
    label = concept.label(language)
    note = next((note for note in concept.notes if note.type == "note"), None)
    source = concept.sources[0] if concept.sources else None
    row = [
        str(concept.id),
        label.label if label else "",
        note.note if note else "",
        source.citation if source else "",
    ]
    cells = _dump(extra_data_dumper, concept)
    for obj in (label, note, source):
        if obj is not None:
            with exception_context(repr(obj)):
                cells.update(_dump(extra_data_dumper, obj))
    row.extend([""] * (max(cells, default=0) + 1 - len(row)))
    for index, cell in cells.items():
        row[index] = cell
    while len(row) > 2 and not row[-1]:
        row.pop()
    return row


def _dump(
    extra_data_dumper: CsvExtraDataDumper, obj: Concept | Label | Note | Source
) -> dict[int, str]:
    try:
        return extra_data_dumper(obj) or {}
    except Exception as err:
        raise ExtraDataException(f"Failed to dump extra_data: {err}") from err
