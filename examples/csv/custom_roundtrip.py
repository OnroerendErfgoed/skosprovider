"""
This example round trips the extra_data of a SimpleCsvProvider with a loader
and a dumper of its own.

The csv has an extra ninth column with the creator of the label. The loader
only keeps that creator. The dumper writes the creator back to the ninth
column and adds a publisher in a tenth column that was not in the input.
"""

import csv
import sys
from pathlib import Path

from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib.namespace import DCTERMS

from skosprovider.csv.dumper import csv_dumper
from skosprovider.csv.provider import SimpleCsvProvider
from skosprovider.extra_data import SkosObject
from skosprovider.skos import Label
from skosprovider.uri import UriPatternGenerator


def load_creator(row: list[str], skos_object: SkosObject) -> Graph | None:
    """Load only the creator of the 9th row for a label."""
    if not isinstance(skos_object, Label) or len(row) <= 8 or not row[8]:
        return None
    graph = Graph()
    graph.add((BNode(), DCTERMS.creator, Literal(row[8])))
    return graph


def dump_creator(obj: SkosObject) -> dict[int, str] | None:
    """Dump the creator to the 9th row and add a fixed publisher."""
    if obj.extra_data is None:
        return None
    creator = next(obj.extra_data.objects(predicate=DCTERMS.creator))
    return {8: str(creator), 9: "Tree Society"}


with open(Path(__file__).parents[1] / "data" / "trees.csv") as file:
    provider = SimpleCsvProvider(
        {"id": "TREES"},
        csv.reader(file),
        uri_generator=UriPatternGenerator("http://id.trees.org/%s"),
        extra_data_loader=load_creator,
    )

dump = csv_dumper(provider, extra_data_dumper=dump_creator)
csv.writer(sys.stdout).writerows(dump)
