# -*- coding: utf-8 -*-
'''
This module contains utility functions for dealing with skos providers.
'''

from skosprovider.skos import (
    Concept,
    Collection
)


def dict_dumper(provider):
    '''
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.providers.FlatDictionaryProvider` or a
    :class:`skosprovider.providers.TreeDictionaryProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a `dict`.
    :rtype: A list of dicts.

    .. versionadded:: 0.2.0
    '''
    ret = []
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        labels = [l.__dict__ for l in c.labels]
        if isinstance(c, Concept):
            notes = [n.__dict__ for n in c.notes]
            ret.append({
                'id': c.id,
                'type': 'concept',
                'labels': labels,
                'notes': notes,
                'narrower': c.narrower,
                'broader': c.broader,
                'related': c.related
            })
        elif isinstance(c, Collection):
            ret.append({
                'id': c.id,
                'type': 'collection',
                'labels': labels,
                'members': c.members
            })
    return ret
