.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   SKOS
    `Simple Knowledge Organization System <http://www.w3.org/2004/02/skos>`__. A
    general specification for Knowledge Organisation Systems (thesauri, word 
    lists, authority files, ...) that is commonly serialised as :term:`RDF`.

   SKOS-THES
    The `ISO 25964 SKOS extension <http://pub.tenforce.com/schemas/iso25964/skos-thes/>`_
    defines mappings between the ISO 25964 standard and the :term:`SKOS` 
    specification.

   RDF
    `Resource Description Framework <http://www.w3.org/RDF/>`__. A very flexible 
    model for data definition organised around `triples`. These triples forms a 
    directed, labeled graph, where the edges represent the named link between 
    two resources, represented by the graph nodes.

   URI
    A `Uniform Resource Identifier`.

   URN
    A URN is a specific form of a :term:`URI`.

   language-tag
    A valid tag from the `IANA language subtag registry <http://www.iana.org/assignments/language-subtag-registry/language-subtag-registry>`__. Eg. `nl-BE`, `en-Latn-GB`, `i-klingon`, `lb`, `zh-latn-pinyin-x-notone`, ... 
    Skosprovider uses the 
    `language-tags <https://pypi.python.org/pypi/language-tags>`__ library 
    to handle the complexities of these tags.
