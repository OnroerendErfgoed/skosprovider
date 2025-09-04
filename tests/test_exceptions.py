from skosprovider.exceptions import ProviderUnavailableException


class TestExceptions:

    def test_provider_unavailable_exception(self):
        exc = ProviderUnavailableException("test error")
        assert "test error" == repr(exc)
