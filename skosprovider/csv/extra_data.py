"""
Loaders and dumpers for the extra_data of skos objects in a csv row.

A csv loader receives the full csv row passed to a
:class:`~skosprovider.csv.provider.SimpleCsvProvider` and the concept, label,
note or source built from it, and returns a :class:`rdflib.Graph` or `None`.

A csv dumper receives a concept, label, note or source and returns the text of
its extra_data cell, or `None`.
:func:`~skosprovider.csv.dumper.csv_dumper` puts it in the column of that type
of object, see :data:`EXTRA_DATA_COLUMNS`.

The loaders and dumpers in this module keep the extra_data in those columns
as a turtle string or as a JSON-LD string. An empty or missing cell has no
extra_data.

:func:`skosprovider.extra_data.ignore` can be used as both a loader and a
dumper and is the default everywhere.
"""

import json
from collections.abc import Callable

from rdflib import Graph

from skosprovider.dictionary.extra_data import from_jsonld as dict_from_jsonld
from skosprovider.dictionary.extra_data import from_turtle as dict_from_turtle
from skosprovider.dictionary.extra_data import to_jsonld as dict_to_jsonld
from skosprovider.dictionary.extra_data import to_turtle as dict_to_turtle
from skosprovider.extra_data import SkosObject
from skosprovider.skos import Concept
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source

CsvExtraDataDumper = Callable[[Concept | Label | Note | Source], str | None]

EXTRA_DATA_COLUMNS = {Concept: 4, Label: 5, Note: 6, Source: 7}
"""
The index of the column with the extra_data of each type of object: the
fifth to eighth column, after `<id>,<preflabel>,<note>,<source>`.
"""


def _cell(row: list[str], skos_object: SkosObject) -> str | None:
    index = EXTRA_DATA_COLUMNS[type(skos_object)]
    return row[index] if len(row) > index and row[index] else None


def from_turtle(row: list[str], skos_object: SkosObject) -> Graph | None:
    """
    Load the turtle string in the extra_data column of the type of the skos
    object, see :data:`EXTRA_DATA_COLUMNS`.

    :returns: A graph, or `None` when the cell is empty or missing.
    """
    cell = _cell(row, skos_object)
    return None if cell is None else dict_from_turtle({"extra_data": cell}, skos_object)


def from_jsonld(row: list[str], skos_object: SkosObject) -> Graph | None:
    """
    Load the JSON-LD string in the extra_data column of the type of the skos
    object, see :data:`EXTRA_DATA_COLUMNS`.

    :returns: A graph, or `None` when the cell is empty or missing.
    """
    cell = _cell(row, skos_object)
    if cell is None:
        return None
    return dict_from_jsonld({"extra_data": json.loads(cell)}, skos_object)


def to_turtle(obj: Concept | Label | Note | Source) -> str | None:
    """
    Dump the extra_data of a skos object as a turtle string.

    :returns: A string, or `None` when the object has no extra_data.
    """
    dumped = dict_to_turtle(obj)
    return None if dumped is None else dumped["extra_data"]


def to_jsonld(obj: Concept | Label | Note | Source) -> str | None:
    """
    Dump the extra_data of a skos object as a compact JSON-LD string, see
    :func:`skosprovider.dictionary.extra_data.to_jsonld`.

    :returns: A string, or `None` when the object has no extra_data.
    """
    dumped = dict_to_jsonld(obj)
    return None if dumped is None else json.dumps(dumped["extra_data"])
