"""
This example loads a list of dicts from a json file into a DictionaryProvider
and dumps the provider to a list of dicts again.
"""

import json
from pathlib import Path

from skosprovider.dictionary.dumper import dict_dumper
from skosprovider.dictionary.provider import DictionaryProvider

with open(Path(__file__).parents[1] / "data" / "trees.json") as file:
    provider = DictionaryProvider({"id": "TREES"}, json.load(file))

dump = dict_dumper(provider)
print(json.dumps(dump, indent=2))
