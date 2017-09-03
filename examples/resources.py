# -*- coding: utf-8 -*-

'''
This example demonstrates handling resources with a registry. This allows
refreshing database connections and such in a threaded web environment.
'''

import os
import time
import csv

from skosprovider.uri import UriPatternGenerator

from skosprovider.providers import SimpleCsvProvider
from skosprovider.registry import Registry
from skosprovider.skos import ConceptScheme

from skosprovider.resources import IResource

class ICsvReaderResource(IResource):
    '''
    Interface for CSV resources need by CsvReaderProvider
    '''
    pass

class CsvReaderProvider(SimpleCsvProvider):

    reader = None

    def __init__(self, metadata, reader, **kwargs):
        '''
        :param metadata: A metadata dictionary.
        :param reader: A csv reader.
        '''
        self.reader = reader
        super(SimpleCsvProvider, self).__init__(metadata, [], **kwargs)
        self._refresh()

    def clear_resources(self):
        self.reader = None
        self.list = []

    def set_resources(self, resources):
        for k,v in resources.items():
            if k.isOrExtends(ICsvReaderResource):
                self.reader = v
                self._refresh()
                break

    def register_resource(self, resource, interface):
        try:
            if interface.isOrExtends(ICsvReaderResource):
                self.reader = resource
                self._refresh()
        except Exception as e:
            for intf in interface:
                if intf.isOrExtends(ICsvReaderResource):
                    self.reader = resource
                    self._refresh()
                    break

    def _refresh(self):
        if self.reader is None:
            raise ResouceUnavailableException('No CSV reader to work with.')
        self.list = [self._from_row(row) for row in self.reader]

def open_file():
    return open(
        os.path.join(os.path.dirname(__file__), '..', 'tests', 'data', 'menu.csv'),
        "r"
    )

def get_reader(ifile):
    return csv.reader(ifile)

def close_file(ifile):
    ifile.close()

ifile = open_file()
reader = get_reader(ifile)

csvprovider = CsvReaderProvider(
    {'id': 'MENU'},
    reader,
    uri_generator=UriPatternGenerator('http://id.python.org/menu/%s'),
    concept_scheme=ConceptScheme('http://id.python.org/menu')
)

reg = Registry()
reg.register_provider(csvprovider)

c1 = csvprovider.get_by_id(1)
print(c1)

reg.clear_resources()
ifile.close()

print('Sleepy now')
time.sleep(2)


ifile2 = open_file()
reader = get_reader(ifile2)

reg.set_resources({ICsvReaderResource: reader})

c1 = csvprovider.get_by_id(1)
print(c1)

reg.clear_resources()
ifile2.close()

print('Sleepy again')
time.sleep(2)

ifile3 = open_file()
reader = get_reader(ifile3)

reg.register_resource(reader, ICsvReaderResource)

c1 = csvprovider.get_by_id(1)
print(c1)

reg.clear_resources()
ifile3.close()

print('Sleepy again and again')
time.sleep(2)

ifile3 = open_file()
reader = get_reader(ifile3)

reg.register_resource(reader, [IResource, ICsvReaderResource])

c1 = csvprovider.get_by_id(1)
print(c1)

print('Ending now')
reg.clear_resources()
ifile3.close()
