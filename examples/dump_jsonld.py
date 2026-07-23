"""
This example demonstrates the skosprovider API with a simple
DictionaryProvider containing just three items.
"""

import json

from pyld import jsonld
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib.namespace import XSD
from skosprovider.jsonld import CONTEXT
from skosprovider.jsonld import to_jsonld
from skosprovider.providers import DictionaryProvider
from skosprovider.skos import ConceptScheme
from skosprovider.skos import Note
from skosprovider.skos import Source
from skosprovider.uri import UriPatternGenerator

DCT = Namespace("http://purl.org/dc/terms/")

# extra_data for a Note: creator and date of the change note
_larch_change_note_uri = URIRef("http://id.trees.org/notes/larch-change-1999")
_larch_change_note_graph = Graph()
_larch_change_note_graph.add(
    (
        _larch_change_note_uri,
        DCT.creator,
        URIRef("http://id.trees.org/persons/HoraceGray"),
    )
)
_larch_change_note_graph.add(
    (_larch_change_note_uri, DCT.date, Literal("1999-01-23", datatype=XSD.date))
)

# extra_data for a Source: creator and date of the source
_larch_source_uri = URIRef("http://id.trees.org/sources/larch-monograph")
_larch_source_graph = Graph()
_larch_source_graph.add(
    (
        _larch_source_uri,
        DCT.creator,
        URIRef("http://id.trees.org/persons/JohnDoe"),
    )
)
_larch_source_graph.add(
    (_larch_source_uri, DCT.date, Literal("2005", datatype=XSD.gYear))
)

# extra_data for the larch Concept itself: creation and modification dates
_larch_uri = URIRef("http://id.trees.org/1")
_larch_concept_graph = Graph()
_larch_concept_graph.add(
    (_larch_uri, DCT.created, Literal("2010-01-15", datatype=XSD.date))
)
_larch_concept_graph.add(
    (_larch_uri, DCT.modified, Literal("2020-06-01", datatype=XSD.date))
)

# extra_data for the species Collection: creation date
_species_uri = URIRef("http://id.python.org/different/types/of/trees")
_species_collection_graph = Graph()
_species_collection_graph.add(
    (_species_uri, DCT.created, Literal("1969", datatype=XSD.gYear))
)
_species_collection_graph.add(
    (
        _species_uri,
        DCT.creator,
        URIRef("http://www.wikidata.org/entity/16402"),
    )
)

# extra_data for the ConceptScheme: creation date
_cs_uri = URIRef("http://id.trees.org")
_cs_graph = Graph()
_cs_graph.add((_cs_uri, DCT.created, Literal("2009-12-01", datatype=XSD.date)))

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
    "notes": [
        {"type": "definition", "language": "en", "note": "A type of tree."},
        Note(
            "Moved from under 'conifers' to under 'deciduous'",
            type="changeNote",
            language="en",
            uri="http://id.trees.org/notes/larch-change-1999",
            extra_data=_larch_change_note_graph,
        ),
    ],
    "sources": [
        {"citation": "Monographs on Trees, vol. 1."},
        Source(
            "The Larch: A Complete Monograph",
            uri="http://id.trees.org/sources/larch-monograph",
            extra_data=_larch_source_graph,
        ),
    ],
    "member_of": ["3"],
    "matches": {
        "close": ["http://id.python.org/different/types/of/trees/nr/1/the/larch"]
    },
    "extra_data": _larch_concept_graph,
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
    "uri": "http://id.python.org/different/types/of/trees",
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
    "extra_data": _species_collection_graph,
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
        extra_data=_cs_graph,
    ),
)

# Generate a doc for a cs
from skosprovider.jsonld import to_jsonld

# doc = jsonld_dumper(provider, CONTEXT)
doc = to_jsonld(provider)
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
