# -*- coding: utf-8 -*-
'''
This module contains utility functions for dealing with skos providers.
'''

from __future__ import unicode_literals

from skosprovider.skos import (
    Concept,
    Collection
)


def dict_dumper(provider):
    '''
    Dump a provider to a format that can be passed to a
    :class:`skosprovider.providers.DictionaryProvider`.

    :param skosprovider.providers.VocabularyProvider provider: The provider
        that wil be turned into a `dict`.
    :rtype: A list of dicts.

    .. versionadded:: 0.2.0
    '''
    ret = []
    for stuff in provider.get_all():
        c = provider.get_by_id(stuff['id'])
        labels = [l.__dict__ for l in c.labels]
        notes = [n.__dict__ for n in c.notes]
        sources = [s.__dict__ for s in c.sources]
        if isinstance(c, Concept):
            ret.append({
                'id': c.id,
                'uri': c.uri,
                'type': c.type,
                'labels': labels,
                'notes': notes,
                'sources': sources,
                'narrower': c.narrower,
                'broader': c.broader,
                'related': c.related,
                'member_of': c.member_of,
                'subordinate_arrays': c.subordinate_arrays,
                'matches': c.matches
            })
        elif isinstance(c, Collection):
            ret.append({
                'id': c.id,
                'uri': c.uri,
                'type': c.type,
                'labels': labels,
                'notes': notes,
                'sources': sources,
                'members': c.members,
                'member_of': c.member_of,
                'superordinates': c.superordinates
            })
    return ret
