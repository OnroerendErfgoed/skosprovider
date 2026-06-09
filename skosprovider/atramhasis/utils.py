"""
Utility functions for :mod:`skosprovider.atramhasis`.
"""

import logging

from skosprovider.skos import Collection
from skosprovider.skos import Concept
from skosprovider.skos import ConceptScheme
from skosprovider.skos import dict_to_label
from skosprovider.skos import dict_to_note
from skosprovider.skos import dict_to_source

log = logging.getLogger(__name__)


def dict_to_thing(data_dict):
    """
    Transform a dict into a
    :class:`skosprovider.skos.Concept` or :class:`skosprovider.skos.Collection`.

    If the argument passed is already a :class:`skosprovider.skos.Concept` or
    :class:`skosprovider.skos.Collection`, this method just returns the argument.
    """
    if isinstance(data_dict, Concept) or isinstance(data_dict, Collection):
        return data_dict
    else:
        if "id" in data_dict:
            id_ = data_dict["id"]
        else:
            raise ValueError("id: No id available in dict")

        if "type" in data_dict:
            type_ = data_dict["type"]
        else:
            raise ValueError("type: type is not defined in dict")

        if type_ == "concept":
            thing = Concept(id_)
            if "subordinate_arrays" in data_dict:
                thing.subordinate_arrays = [
                    n["id"] for n in data_dict["subordinate_arrays"]
                ]
            if "matches" in data_dict:
                matches = data_dict["matches"]
                for match_type in thing.matchtypes:
                    if match_type in matches:
                        thing.matches[match_type] = matches[match_type]
        elif type_ == "collection":
            thing = Collection(id_)
            if "superordinates" in data_dict:
                thing.superordinates = [n["id"] for n in data_dict["superordinates"]]
            if "members" in data_dict:
                thing.members = [n["id"] for n in data_dict["members"]]
        else:
            raise ValueError(
                "type: type is not valid ('concept', 'collection') in dict"
            )
        thing.type = type_
        thing.uri = data_dict["uri"] if "uri" in data_dict else None
        thing.concept_scheme = (
            ConceptScheme(data_dict["concept_scheme"])
            if "concept_scheme" in data_dict
            else None
        )
        if "labels" in data_dict:
            thing.labels = [(dict_to_label(l)) for l in data_dict["labels"]]
        if "notes" in data_dict:
            thing.notes = [(dict_to_note(n)) for n in data_dict["notes"]]
        if "sources" in data_dict:
            thing.sources = [(dict_to_source(n)) for n in data_dict["sources"]]
        if "narrower" in data_dict:
            thing.narrower = [n["id"] for n in data_dict["narrower"]]
        if "broader" in data_dict:
            thing.broader = [n["id"] for n in data_dict["broader"]]
        if "related" in data_dict:
            thing.related = [n["id"] for n in data_dict["related"]]
        if "member_of" in data_dict:
            thing.member_of = [n["id"] for n in data_dict["member_of"]]
        return thing
