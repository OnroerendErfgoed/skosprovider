"""
Utility functions for caching in :mod:`skosprovider.atramhasis`.
"""

import functools
import json


def _atramhasis_key_generator(namespace, fn, to_str=str):
    """
    This is mostly a copy of dogpile.cache.util.function_key_generator.

    The main difference is that it adds the provider's `base_url` and
    `scheme_id` as part of the cache key, so that different providers
    don't use each other's caches. As well as we try and handle kwargs.
    """
    if namespace is None:
        namespace = f"{fn.__module__}:{fn.__name__}"
    else:
        namespace = f"{fn.__module__}:{fn.__name__}|{namespace}"

    def generate_key(*args, **kwargs):
        provider = args[0]
        args = (
            [provider.base_url, provider.scheme_id]
            + list(args[1:])
            + [json.dumps(kwargs, sort_keys=True)]
        )
        return namespace + "|" + " ".join(map(to_str, args))

    return generate_key


def _dont_cache_false(value):
    """
    Returns True when the value should be cached.

    Because the provider can return False in error cases, we must prevent False
    from being cached by dogpile.
    """
    return value is not False


def _cache_on_arguments(cache_name, expiration_time=None):
    """
    Cache a method call in a cache region found in `self.caches[cache_name]`.

    The first parameter of the cached method is assumed to be the "self".

    In this `self` object the attribute "caches" will be taken. This is
    assumed to be a dict. This dict must have the `cache_name` key with
    a dogpile region as value.
    """

    def decorator(fn):
        key_generator = _atramhasis_key_generator(None, fn)

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            self = args[0]
            key = key_generator(*args, **kwargs)
            return self.caches[cache_name].get_or_create(
                key, fn, expiration_time, _dont_cache_false, (args, kwargs)
            )

        return wrapped

    return decorator
