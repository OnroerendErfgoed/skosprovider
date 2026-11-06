"""
This module provides a provider that reads a simple csv format into memory.
"""

from collections.abc import Iterable
from typing import Any

from skosprovider.extra_data import ExtraDataLoader
from skosprovider.extra_data import exception_context
from skosprovider.extra_data import ignore
from skosprovider.extra_data import load_extra_data
from skosprovider.provider import MemoryProvider
from skosprovider.skos import Concept
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source


class SimpleCsvProvider(MemoryProvider):
    """
    A provider that reads a simple csv format into memory.

    The supported csv format looks like this:
    <id>,<preflabel>,<note>,<source>

    The extra_data loaders in :mod:`skosprovider.csv.extra_data` read the
    extra_data of the concept, label, note and source from four extra
    columns, as written by :func:`~skosprovider.csv.dumper.csv_dumper`.

    This provider essentialy provides a flat list of concepts. This is commonly
    associated with short lookup-lists.

    .. versionadded:: 0.2.0
    """

    def __init__(
        self,
        metadata: dict[str, Any],
        reader: Iterable[list[str]],
        *,
        concept_extra_data_loader: ExtraDataLoader = ignore,
        label_extra_data_loader: ExtraDataLoader = ignore,
        note_extra_data_loader: ExtraDataLoader = ignore,
        source_extra_data_loader: ExtraDataLoader = ignore,
        **kwargs: Any,
    ) -> None:
        """
        Every extra_data loader receives the full csv row (a list) and returns
        a :class:`rdflib.Graph` or `None`. See :mod:`skosprovider.csv.extra_data`
        for the available loaders. They all default to
        :func:`~skosprovider.extra_data.ignore`.

        :param metadata: A metadata dictionary.
        :param reader: A csv reader.
        :param concept_extra_data_loader: Loads the extra_data of the concept.
        :param label_extra_data_loader: Loads the extra_data of the label.
        :param note_extra_data_loader: Loads the extra_data of the note. Only
            called when the row has a note.
        :param source_extra_data_loader: Loads the extra_data of the source.
            Only called when the row has a source.
        """
        super().__init__(metadata, [], **kwargs)
        self.concept_extra_data_loader = concept_extra_data_loader
        self.label_extra_data_loader = label_extra_data_loader
        self.note_extra_data_loader = note_extra_data_loader
        self.source_extra_data_loader = source_extra_data_loader
        self.list = [self._from_row(row) for row in reader]

    def _from_row(self, row: list[str]) -> Concept:
        id = row[0]
        with exception_context(f"concept {id!r}"):
            labels = [Label(row[1], "prefLabel")]
            for label in labels:
                with exception_context(repr(label)):
                    label.extra_data = load_extra_data(
                        self.label_extra_data_loader, row
                    )

            if len(row) > 2 and row[2]:
                notes = [Note(row[2], "note")]
            else:
                notes = []
            for note in notes:
                with exception_context(repr(note)):
                    note.extra_data = load_extra_data(self.note_extra_data_loader, row)

            if len(row) > 3 and row[3]:
                sources = [Source(row[3])]
            else:
                sources = []
            for source in sources:
                with exception_context(repr(source)):
                    source.extra_data = load_extra_data(
                        self.source_extra_data_loader, row
                    )

            return Concept(
                id=id,
                uri=self.uri_generator.generate(type="concept", id=id),
                labels=labels,
                notes=notes,
                sources=sources,
                extra_data=load_extra_data(self.concept_extra_data_loader, row),
            )
