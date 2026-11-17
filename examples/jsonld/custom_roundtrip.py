"""
This example round trips the extra_data of a JsonLdProvider with a loader and
a dumper of its own.

The loader only keeps the dct:creator of a SKOS-XL label and ignores
everything else. The dumper writes the creator back and adds a dct:publisher
that was not in the input.
"""

import json
from pathlib import Path
from typing import Any

from rdflib import Graph
from rdflib.namespace import DCTERMS

from skosprovider.extra_data import SkosObject
from skosprovider.jsonld.dumper import to_jsonld
from skosprovider.jsonld.extra_data import jsonld_to_graph
from skosprovider.jsonld.provider import JsonLdProvider
from skosprovider.skos import Label


def load_creator(node: dict[str, Any], skos_object: SkosObject) -> Graph | None:
    """Load only the creator of a label."""
    creators = node.get(str(DCTERMS.creator))
    if not isinstance(skos_object, Label) or not creators:
        return None
    return jsonld_to_graph({"@id": node["@id"], str(DCTERMS.creator): creators})


def dump_creator(obj: SkosObject) -> dict[str, Any] | None:
    """Dump the creator and add a fixed publisher."""
    if obj.extra_data is None:
        return None
    return {
        "dct:creator": [str(creator) for creator in obj.extra_data.objects()],
        "dct:publisher": "Tree Society",
    }


with open(Path(__file__).parents[1] / "data" / "trees.jsonld") as file:
    provider = JsonLdProvider(
        {"id": "TREES"}, json.load(file), extra_data_loader=load_creator
    )

dump = to_jsonld(provider, extra_data_dumper=dump_creator)
print(json.dumps(dump, indent=2))
