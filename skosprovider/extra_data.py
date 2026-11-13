"""
Shared building blocks for the extra_data of skos objects.

In the skos model, extra_data is always a :class:`rdflib.Graph` or `None`.

A loader receives the input of a single object, eg. a dict, a csv row or an RDF
node, and returns a :class:`rdflib.Graph` or `None`. The loaders and dumpers
for a specific input format live next to the provider that reads it, eg.
:mod:`skosprovider.dictionary.extra_data` and :mod:`skosprovider.rdf.extra_data`.

:func:`ignore` can be used as both a loader and a dumper and is the default
everywhere.
"""

from collections.abc import Callable
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from rdflib import Graph

from skosprovider.exceptions import ExtraDataException
from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import Label
from skosprovider.skos import Note
from skosprovider.skos import Source

SkosObject = Concept | Collection | Label | Note | Source
ExtraDataLoader = Callable[[Any], Graph | None]


def ignore(*_: object) -> None:
    """
    An extra_data loader or dumper that ignores all extra_data.

    :returns: Always `None`.
    """
    return None


def load_extra_data(loader: ExtraDataLoader, data: Any) -> Graph | None:
    """
    Call a loader and wrap any error in an :class:`ExtraDataException`.

    Use :func:`exception_context` to describe which object was being loaded.

    :returns: A :class:`rdflib.Graph` or `None`.
    """
    try:
        return loader(data)
    except Exception as err:
        raise ExtraDataException(f"Failed to load extra_data: {err}") from err


@contextmanager
def exception_context(description: str) -> Iterator[None]:
    """
    Describe which object is being processed when an
    :class:`ExtraDataException` passes through.

    The description is added as a note (:pep:`678`) to the exception. Nested
    contexts add one note each, innermost first.

    :param description: Describes the object, eg. `concept '1'`.
    """
    try:
        yield
    except ExtraDataException as err:
        err.add_note(f"while processing {description}")
        raise
