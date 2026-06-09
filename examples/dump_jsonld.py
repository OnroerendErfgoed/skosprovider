"""
This example demonstrates the skosprovider API with a simple
DictionaryProvider containing just three items.

Extra data is attached to a label, a note, and a concept to show how
custom context entries and a serializer can round-trip application-specific
properties through JSON-LD.
"""

import json

from pyld import jsonld
from skosprovider.jsonld import CONTEXT
from skosprovider.jsonld import SkosObject
from skosprovider.jsonld import jsonld_dumper
from skosprovider.providers import DictionaryProvider
from skosprovider.skos import ConceptScheme
from skosprovider.uri import UriPatternGenerator

# Extended context: copy CONTEXT and map application-specific keys to URIs.
# Note: keys used inside label/note objects (which expand to @value nodes) cannot
# be mapped here — JSON-LD forbids extra properties alongside @value.  Those keys
# (source_system, source_citation) are left unmapped so they are treated as
# opaque application data and are dropped by JSON-LD processors during expansion.
CUSTOM_CONTEXT = {
    **CONTEXT,
    "notation": {"@id": "skos:notation", "@container": "@set"},
    "source_system": {"@id": "dct:source"},
}


def extra_data_serializer(doc: dict, obj: SkosObject) -> None:
    """Merge extra_data dict into doc; keys are mapped in CUSTOM_CONTEXT."""
    if isinstance(obj.extra_data, dict):
        doc.update(obj.extra_data)


larch = {
    "id": "1",
    "uri": "http://id.trees.org/1",
    "labels": [
        {
            "uri": "http://id.trees.org/labels/larch-en",
            "type": "prefLabel",
            "language": "en",
            "label": "The Larch",
            "source_system": "legacy_db",  # extra_data on xl Label
        },
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
    "notes": [
        {
            "type": "definition",
            "language": "en",
            "note": "A type of tree.",
            "source_citation": "Botanical Dictionary, 2nd ed.",  # extra_data on Note
        }
    ],
    "member_of": ["3"],
    "matches": {
        "close": ["http://id.python.org/different/types/of/trees/nr/1/the/larch"]
    },
    "notation": ["larch-001"],  # extra_data on Concept, maps to skos:notation
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

# classic json-ld dumper with minimal skos info.
doc = jsonld_dumper(provider)
msg = "Conceptscheme without extra data"
print(msg)
print(len(msg) * "=")
print(json.dumps(doc, indent=2))

# Generate a doc with custom context and serializer
doc = jsonld_dumper(
    provider, CUSTOM_CONTEXT, extra_data_serializer=extra_data_serializer
)
msg = "Conceptscheme with extra data"
print(msg)
print(len(msg) * "=")
print(json.dumps(doc, indent=2))

# Print an expanded doc
expanded = jsonld.expand(doc, CUSTOM_CONTEXT)
msg = "Conceptscheme expanded"
print(msg)
print(len(msg) * "=")
print(json.dumps(expanded, indent=2))

# Compact the doc again
compacted = jsonld.compact(expanded, CUSTOM_CONTEXT)
msg = "Conceptscheme compacted again"
print(msg)
print(len(msg) * "=")
print(json.dumps(compacted, indent=2))

# And now flatten it
flattened = jsonld.flatten(compacted, CUSTOM_CONTEXT)
msg = "Conceptscheme flattened"
print(msg)
print(len(msg) * "=")
print(json.dumps(flattened, indent=2))
