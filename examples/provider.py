"""
This example demonstrates the skosprovider API with a DictionaryProvider
loaded from a json file. Every provider has the same API.
"""

import json
from pathlib import Path

from skosprovider.dictionary.provider import DictionaryProvider

with open(Path(__file__).parent / "data" / "trees.json") as file:
    provider = DictionaryProvider(
        {"id": "TREES", "default_language": "en"}, json.load(file)
    )

# Get a concept or collection by id
print(provider.get_by_id("1").label().label)

# Get a concept or collection by uri
print(provider.get_by_uri("http://id.trees.org/1"))

# Get all concepts and collections in a provider
# If possible, show a Dutch(as spoken in Belgium) label
# Order them ascending by label
print(provider.get_all(language="nl-BE", sort="label", sort_order="asc"))

# Get the top concepts in a provider
print(provider.get_top_concepts())

# Find anything that has a label of The Larch
print(provider.find({"label": "The Larch"}))

# Get the top of a display hierarchy
print(provider.get_top_display())

# Get the children to display in a hierarchy
# If possible, show a French, Dutch or English label
# Order them descending by id
print(
    provider.get_children_display(
        "3", language=["fr-BE", "nl-BE", "en"], sort="id", sort_order="desc"
    )
)

# Get all concepts underneath a concept or collection
print(provider.expand("3"))
