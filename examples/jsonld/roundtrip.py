"""
This example loads a JSON-LD file into a JsonLdProvider and dumps the
provider to JSON-LD again.
"""

import json
from pathlib import Path

from skosprovider.jsonld.dumper import to_jsonld
from skosprovider.jsonld.provider import JsonLdProvider

with open(Path(__file__).parents[1] / "data" / "trees.jsonld") as file:
    provider = JsonLdProvider({"id": "TREES"}, json.load(file))

dump = to_jsonld(provider)
print(json.dumps(dump, indent=2))
