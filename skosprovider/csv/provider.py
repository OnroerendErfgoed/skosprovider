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
        extra_data_loader: ExtraDataLoader = ignore,
        **kwargs: Any,
    ) -> None:
        """
        :param metadata: A metadata dictionary.
        :param reader: A csv reader.
        :param extra_data_loader: A callable that receives the full csv row (a
            list) and the concept, label, note or source built from it, and
            returns a :class:`rdflib.Graph` or `None`. It is called for the
            note and the source only when the row has one. See
            :mod:`skosprovider.csv.extra_data` for the available loaders.
            Defaults to :func:`~skosprovider.extra_data.ignore`.
        """
        super().__init__(metadata, [], **kwargs)
        self.extra_data_loader = extra_data_loader
        self.list = [self._from_row(row) for row in reader]

    def _from_row(self, row: list[str]) -> Concept:
        id = row[0]
        with exception_context(f"concept {id!r}"):
            labels = [Label(row[1], "prefLabel")]
            for label in labels:
                with exception_context(repr(label)):
                    label.extra_data = load_extra_data(
                        self.extra_data_loader, row, label
                    )

            if len(row) > 2 and row[2]:
                notes = [Note(row[2], "note")]
            else:
                notes = []
            for note in notes:
                with exception_context(repr(note)):
                    note.extra_data = load_extra_data(self.extra_data_loader, row, note)

            if len(row) > 3 and row[3]:
                sources = [Source(row[3])]
            else:
                sources = []
            for source in sources:
                with exception_context(repr(source)):
                    source.extra_data = load_extra_data(
                        self.extra_data_loader, row, source
                    )

            concept = Concept(
                id=id,
                uri=self.uri_generator.generate(type="concept", id=id),
                labels=labels,
                notes=notes,
                sources=sources,
            )
            concept.extra_data = load_extra_data(self.extra_data_loader, row, concept)
            return concept
