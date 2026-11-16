"""This module provides custom exceptions for skos providers.

.. versionadded:: 0.5.0
"""


class SkosproviderException(Exception):
    """
    Base class for all exceptions raised by skosprovider.
    """


class ProviderUnavailableException(SkosproviderException):
    """
    This exception can be raised by a provider if it's unable to provide
    the thesaurus. This can occur when an underlying resource is unavailable
    (database connection, webservice, ...). The message should contain some
    more information about the problem.
    """

    def __init__(self, message):
        """
        :param message: More information about the exception.
        """
        self.message = message

    def __repr__(self):
        return self.message


class InvalidDataException(SkosproviderException, ValueError):
    """
    Raised when data passed to skosprovider is not valid.

    Extends :class:`ValueError` for backwards compatibility.
    """


class ConceptSchemeException(SkosproviderException, RuntimeError):
    """
    Raised when a provider can not determine which conceptscheme to use.

    Extends :class:`RuntimeError` for backwards compatibility.
    """


class NotFoundException(SkosproviderException, LookupError):
    """
    Raised when a concept or collection could not be found.
    """


class ExtraDataException(SkosproviderException):
    """
    Raised when loading or dumping the extra_data of a skos object fails.

    The original error is available as `__cause__`.
    """

    def __init__(self, message: str) -> None:
        """
        :param message: Which object failed and whether it was loading or
            dumping.
        """
        super().__init__(message)
        self.message = message
