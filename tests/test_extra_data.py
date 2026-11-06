from rdflib import Graph

from skosprovider.exceptions import ExtraDataException
from skosprovider.exceptions import ProviderUnavailableException
from skosprovider.exceptions import SkosproviderException
from skosprovider.extra_data import ignore


def test_ignore():
    assert ignore({"extra_data": Graph()}) is None


def test_exception_hierarchy():
    assert issubclass(ExtraDataException, SkosproviderException)
    assert issubclass(ProviderUnavailableException, SkosproviderException)
