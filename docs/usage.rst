.. _usage:

Usage
=====

The basic idea of Skosprovider is very much about the idea of `loose coupling`,
allowing two pieces of software to talk to each other while having as little
knowledge of each other as possible. In this case, software A (eg. a webapp)
can make use of 1 or more thesauri, controlled vocabularies, authority files
and other vocabularies without have to no the details of the vocabularies.

This has been achieved by defining an interface of the most common operations
needed to integrate an vocabulary in an application. It's complex and rich 
enough to allow for most operations that an application might need. And of 
course, in special cases you might consider expanding the interface. If you do
so, please let us know. Your needs might be similar to someone else's needs
and might warrant an extension to the interface.

While the interface is very clear on the operations supported and the data it
shoudl receive from the provider, it makes not statement whatsoever about the
format the data should be in when the provider receives it. So, while a client
knows that each provider has a method to find a concept by an id and what this 
method will return, the client does not need to know where the provider goes
to find this concept. One provider might look this up in a 
:class:`CSV file <skosprovider.providers.SimpleCsvProvider>`,
another one in a :class:`database <skosprovider_sqlalchemy.providers.SQLAlchemyProvider>` 
and yet another one through a 
:class:`webservice <skosprovider_heritagedata.providers.HeritagedataProvider>`.
In a way, the provider transforms the data from the source format to a common
view of the :mod:`SKOS data model <skosprovider.skos>`.

Because of this, the only part where the different providers are different is
when instantiating the provider, since they need to be configured for their 
data source. Eg., the :class:`skosprovider.providers.DictionaryProvider` is
a very simple provider that requires a list of dictionaries to operate on.
Apart from this one very specific data element, there are a few configuration
:meth:`parameters <skosprovider.providers.VocabularyProvider.__init__>` that 
are passed to every existing provider. Every provider requires that a 
parameter `metadata` is passed to it. This is a dictionary that has one 
required parameter, `id`. This is an id that is assigned to the provider. It's
used when registering the provider with a :class:`skosprovider.registry.Registry`
and for a few other things. Other than this required parameter, a `metadata`
object can also set a `default_language` for the provider and register a number
of `subjects` for the provider.

Upon instantiation, a provider can also be passed a 
:class:`skosprovider.uri.UriGenerator`. This is an object that allows the 
provider to generate :term:`URI's <URI>` for it's concepts and collections. If
you do not pass in a uri generator, the provider will set one up for you. 
Finally, you can also pass in a :class:`skosprovider.skos.ConceptScheme`. This
is the concept scheme the providers represents. Again, if you do no pass in a
concept scheme, the provider will create a default scheme.

.. code-block:: python

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

Providing you have gotten hold of a Skosprovider, you now have an object with
several methods. Largely these can mainly be grouped into a two 
different categories:

First there are methods that return a single :class:`skosprovider.skos.Concept` or 
:class:`skosprovider.skos.Collection`. These methods allow you to retrieve
an individual item based on one of two possible identifiers.

The first method, 
:meth:`~skosprovider.providers.VocabularyProvider.get_by_id`, 
retrieves an item based on an id that is known internally by the provider. This
id is not necessarily globally unique. It's only required to be unique to a 
certain provider.

The second method, 
:meth:`~skosprovider.providers.VocabularyProvider.get_by_uri`, 
retrieves an item based on it's :term:`URI`. Since a :term:`URI` is guaranteed
to be globally unique. Quite often the :term:`URI` wil also contain the `id`,
but this is not mandatory.

.. code-block:: python

    # Get a concept or collection by id
    provider.get_by_id(1)

    # Get a concept or collection by uri
    provider.get_by_uri('http://id.trees.org/types/1')


A second group of methods return a list of concepts or collections. In this 
case the concepts or collections are only partially output. For each concept or
collection an ``id``, ``uri``, ``type`` (`concept` or `collection`) 
and a ``label`` are returned. Each of these methods also takes an optional
keyword ``language`` that detemines in what language a label is rendered. A
second optional keyword, `sort` allows the client to specify how the list should
be sorted. Options here are ``id``, ``label`` and ``sortlabel``. This last
parameter allows sorting on a special ``sortLabel`` that can be assigned to
concepts and collections. This way, arbitrary sorting order can be created by
the editor of a scheme. When sorting, the `sort_order` keyword can be used to
set the sort order.

One method, :meth:`~skosprovider.providers.VocabularyProvider.get_all`
returns all concept and collections in a certain provider. It's rarely used
and might possibly not make sense in very large providers. It's mainly there
as a convenience method for small providers and in testing situations. More
useful is :meth:`~skosprovider.providers.VocabularyProvider.get_top_concepts`.
This methods returns all top concepts (not collections) in the provider. These
are the concepts that have no 
:attr:`broader concepts <skosprovider.skos.Concept.broader>`.

There are also two related methods that can help in building a display
hierarchy. As opposed to :meth:`~skosprovider.providers.VocabularyProvider.get_top_concepts`,
these do return both concepts and collections and can thus actually be used
to create a sensible display hierarchy for a vocabulary. The first one,
:meth:`~skosprovider.providers.VocabularyProvider.get_top_display`, returns
the top of a display hierarchy. These would be the concepts and collections
that form the top of this hierarchy. To descend the hierachy, you would call
:meth:`~skosprovider.providers.VocabularyProvider.get_children_display`.

A final method in this group of methods is actually the most important one
in this group. By calling :meth:`skosprovider.providers.VocabularyProvider.find`,
you can search the provider for concepts or collections matching your criteria.
You do this by passing in a ``query`` parameter to this method. This way you
can ask the provider to search for certain labels (eg. `churches`), to only
search certain types (concept or collection) or to only search within a cerain
collection. As always in this category of methods, you can control in what 
languages labels should be returned using the ``language`` keyword.

.. code-block:: python

    # Get all concepts and collections in a provider
    # If possible, show a Dutch(as spoken in Belgium) label
    provider.get_all(language='nl-BE')

    # Get all concepts and collections in a provider
    # If possible, show a Dutch(as spoken in Belgium) label 
    # and order them by this label
    provider.get_all(language='nl-BE', sort='label', sort_order='asc')

    # Get the top concepts in a provider
    provider.get_top_concepts()

    # Find anything that has a label of church.
    provider.find({'label': 'church'})

    # Get the top of a display hierarchy
    provider.get_top_display(sort='id', sort_order='desc')

    # Get the children to display in a hierarchy concept 1
    # If possible, show a French(as spoken in Belgium) label
    provider.get_children_display(1, language='fr-BE')

Apart from the two categories, there are a couple more miscellaneous methods. 
The most interesting one of these is 
:meth:`skosprovider.providers.VocabularyProvider.expand`. This methods take
a certain concept or collection id as argument and returns a list of all
concept ids that are "underneath" this concept or collection. This is mainly
intended to be used when querying datasets. It allows a client to broaden the
scope of a search. Eg. when searching for ``churches``, the expand method
might return the ids for both ``churches`` and ``cathedrals``.

.. code-block:: python

    # Get all concepts underneath a concept or collection
    provider.expand(1)
