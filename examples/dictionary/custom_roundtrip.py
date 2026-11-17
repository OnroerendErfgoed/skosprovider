"""
This example round trips the extra_data of a DictionaryProvider with a
loader and a dumper of its own.

The loader only keeps the creator under the `extra_data` key of a label and
ignores everything else. The dumper writes the creator back and adds a
publisher that was not in the input.
"""

import json
from pathlib import Path
from typing import Any

from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.namespace import DCTERMS

from skosprovider.dictionary.dumper import dict_dumper
from skosprovider.dictionary.provider import DictionaryProvider
from skosprovider.extra_data import SkosObject
from skosprovider.skos import Label


def load_creator(data: dict[str, Any], skos_object: SkosObject) -> Graph | None:
    """Load only the creator of a label."""
    creator = data.get("extra_data", {}).get("creator")
    if not isinstance(skos_object, Label) or not skos_object.uri or creator is None:
        return None
    graph = Graph()
    graph.add((URIRef(skos_object.uri), DCTERMS.creator, Literal(creator)))
    return graph


def dump_creator(obj: SkosObject) -> dict[str, Any] | None:
    """Dump the creator and add a fixed publisher."""
    if obj.extra_data is None or not obj.uri:
        return None
    creator = obj.extra_data.value(URIRef(obj.uri), DCTERMS.creator)
    return {"extra_data": {"creator": str(creator), "publisher": "Tree Society"}}


with open(Path(__file__).parents[1] / "data" / "trees.json") as file:
    provider = DictionaryProvider(
        {"id": "TREES"}, json.load(file), extra_data_loader=load_creator
    )

dump = dict_dumper(provider, extra_data_dumper=dump_creator)
print(json.dumps(dump, indent=2))
