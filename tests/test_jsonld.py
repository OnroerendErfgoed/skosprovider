# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from skosprovider.jsonld import (
    jsonld_c_dumper
)

from test_providers import (
    larch,
    species,
    trees,
    geo
)

class TestJsonLdCDumper():

    def test_dump_larch(self):
        doc = jsonld_c_dumper(trees, 1)
        assert doc['id'] == '1'
        assert doc['uri'] == 'http://id.trees.org/1'
        assert doc['type'] == 'concept'
        assert type(doc['label']) == str
        assert len(doc['labels']['pref_labels']) == 2
        assert {
                'language': 'en',
                '@language': 'en',
                'lbl': 'The Larch'
        } in doc['labels']['pref_labels']
        assert len(doc['notes']['definitions']) == 1
        assert {
                'language': 'en',
                '@language': 'en',
                'nt': 'A type of tree.',
        } in doc['notes']['definitions']
        assert len(doc['sources']) == len(larch['sources'])
        assert {
            'citations': [{
                'ct': 'Monthy Python. Episode Three: How to recognise different types of trees from quite a long way away.'
            }]
        } in doc['sources']

    def test_dump_chestnut(self):
        doc = jsonld_c_dumper(trees, 2)
        assert doc['id'] == '2'
        assert doc['uri'] == 'http://id.trees.org/2'
        assert doc['type'] == 'concept'
        assert type(doc['label']) == str
        assert len(doc['labels']['pref_labels']) == 1
        assert {
                'language': 'en',
                '@language': 'en',
                'lbl': 'The Chestnut'
        } in doc['labels']['pref_labels']
        assert len(doc['labels']['alt_labels']) == 2
        assert len(doc['notes']['definitions']) == 1
        assert {
                'language': 'en',
                '@language': 'en',
                'nt': 'A different type of tree.',
        } in doc['notes']['definitions']

    def test_dump_species(self):
        doc = jsonld_c_dumper(trees, 3)
        assert doc['id'] == 3
        assert doc['uri'] == 'http://id.trees.org/3'
        assert doc['type'] == 'collection'
        assert type(doc['label']) == str
        assert len(doc['labels']['pref_labels']) == 2
        assert {
                'language': 'en',
                '@language': 'en',
                'lbl': 'Trees by species'
        } in doc['labels']['pref_labels']
        assert len(doc['labels']['hidden_labels']) == 1
        assert len(doc['notes']['editorial_notes']) == 1
        assert {
                'language': 'en',
                'nt': 'As seen in <em>How to Recognise Different Types of Trees from Quite a Long Way Away</em>.',
                'markup': 'HTML'
        } in doc['notes']['editorial_notes']
