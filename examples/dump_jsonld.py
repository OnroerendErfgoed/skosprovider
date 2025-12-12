"""
This example demonstrates the skosprovider API with a simple
DictionaryProvider containing just three items.
"""

import json

from pyld import jsonld

from skosprovider.jsonld import (
    CONTEXT,
    jsonld_dumper,
)
from skosprovider.providers import DictionaryProvider
from skosprovider.skos import ConceptScheme
from skosprovider.uri import UriPatternGenerator


larch = {
    "id": "1",
    "uri": "http://id.trees.org/1",
    "labels": [
        {"type": "prefLabel", "language": "en", "label": "The Larch"},
        {
            "uri": "http://id.trees.org/labels/lariks-nl",
            "type": "prefLabel",
            "language": "nl",
            "label": "De Lariks",
            "label_types": [
                "http://publications.europa.eu/resource/authority/label-type/STANDARDLABEL"
            ],
        },
    ],
    "notes": [{"type": "definition", "language": "en", "note": "A type of tree."}],
    "member_of": ["3"],
    "matches": {
        "close": ["http://id.python.org/different/types/of/trees/nr/1/the/larch"]
    },
}

chestnut = {
    "id": "2",
    "uri": "http://id.trees.org/2",
    "labels": [
        {"type": "prefLabel", "language": "en", "label": "The Chestnut"},
        {"type": "altLabel", "language": "nl", "label": "De Paardekastanje"},
        {"type": "altLabel", "language": "fr", "label": "la châtaigne"},
    ],
    "notes": [
        {"type": "definition", "language": "en", "note": "A different type of tree."}
    ],
    "member_of": ["3"],
    "matches": {
        "related": [
            "http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut"
        ]
    },
}

species = {
    "id": 3,
    "uri": "http://id.trees.org/3",
    "labels": [
        {"type": "prefLabel", "language": "en", "label": "Trees by species"},
        {"type": "prefLabel", "language": "nl", "label": "Bomen per soort"},
    ],
    "type": "collection",
    "members": ["1", "2"],
    "notes": [
        {
            "type": "editorialNote",
            "language": "en",
            "note": "As seen in <em>How to Recognise Different Types of "
            "Trees from Quite a Long Way Away</em>.",
            "markup": "HTML",
        }
    ],
}

provider = DictionaryProvider(
    {
        "id": "TREES",
        "default_language": "nl",
        "subject": ["biology"],
        "dataset": {"uri": "http://id.trees.org/dataset"},
    },
    [larch, chestnut, species],
    uri_generator=UriPatternGenerator("http://id.trees.org/types/%s"),
    concept_scheme=ConceptScheme(
        "http://id.trees.org",
        labels=[
            {
                "type": "prefLabel",
                "language": "en",
                "label": "Trees",
                "uri": "http://id.trees.org/labels/trees-en",
            },
            {
                "type": "prefLabel",
                "language": "nl",
                "label": "Bomen",
                "uri": "http://id.trees.org/labels/bomen-nl",
            },
        ],
    ),
)

# Generate a doc for a cs
doc = jsonld_dumper(provider, CONTEXT)
msg = "Conceptscheme"
print(msg)
print(len(msg) * "=")
print(json.dumps(doc, indent=2))

# Print an expanded doc
expanded = jsonld.expand(doc, CONTEXT)
msg = "Conceptscheme expanded"
print(msg)
print(len(msg) * "=")
print(json.dumps(expanded, indent=2))

# Compact the doc again
compacted = jsonld.compact(expanded, CONTEXT)
msg = "Conceptscheme compacted again"
print(msg)
print(len(msg) * "=")
print(json.dumps(compacted, indent=2))

# And now flatten it
flattened = jsonld.flatten(compacted, CONTEXT)
msg = "Conceptscheme flattened"
print(msg)
print(len(msg) * "=")
print(json.dumps(flattened, indent=2))
