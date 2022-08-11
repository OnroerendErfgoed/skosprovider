'''
This example demonstrates the skosprovider API with a simple
DictionaryProvider containing just three items.
'''

from skosprovider.providers import DictionaryProvider
from skosprovider.uri import UriPatternGenerator
from skosprovider.skos import ConceptScheme

larch = {
    'id': '1',
    'uri': 'http://id.trees.org/1',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'}
    ],
    'notes': [
        {'type': 'definition', 'language': 'en', 'note': 'A type of tree.'}
    ],
    'member_of': ['3'],
    'matches': {
        'close': ['http://id.python.org/different/types/of/trees/nr/1/the/larch']
    }
}

chestnut = {
    'id': '2',
    'uri': 'http://id.trees.org/2',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'},
        {'type': 'altLabel', 'language': 'nl', 'label': 'De Paardekastanje'},
        {'type': 'altLabel', 'language': 'fr', 'label': 'la châtaigne'}
    ],
    'notes': [
        {
            'type': 'definition', 'language': 'en',
            'note': 'A different type of tree.'
        }
    ],
    'member_of': ['3'],
    'matches': {
        'related': ['http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut']
    }
}

species = {
    'id': 3,
    'uri': 'http://id.trees.org/3',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'}
    ],
    'type': 'collection',
    'members': ['1', '2'],
    'notes': [
        {
            'type': 'editorialNote',
            'language': 'en',
            'note': 'As seen in <em>How to Recognise Different Types of Trees from Quite a Long Way Away</em>.',
            'markup': 'HTML'
        }
    ]
}

provider = DictionaryProvider(
    {
        'id': 'TREES',
        'default_language': 'nl',
        'subject': ['biology']
    },
    [larch, chestnut, species],
    uri_generator=UriPatternGenerator('http://id.trees.org/types/%s'),
    concept_scheme=ConceptScheme('http://id.trees.org')
)

# Get a concept or collection by id
print(provider.get_by_id(1).label().label)

# Get a concept or collection by uri
print(provider.get_by_uri('http://id.trees.org/types/1'))

# Get all concepts and collections in a provider
# If possible, show a Dutch(as spoken in Belgium) label
# Order them ascending by label
print(provider.get_all(language='nl-BE', sort='label', sort_order='asc'))

# Get the top concepts in a provider
print(provider.get_top_concepts())

# Find anything that has a label of horse
print(provider.find({'label': 'The Larch'}))

# Get the top of a display hierarchy
print(provider.get_top_display())

# Get the children to display in a hierarchy
# If possible, show a French, Dutch or German label
# Order them descending by id
print(provider.get_children_display(3, language=['fr-BE', 'nl-BE', 'de-BE'], sort='id', sort_order='desc'))

# Get all concepts underneath a concept or collection
print(provider.expand(3))
