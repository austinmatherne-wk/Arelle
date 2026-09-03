"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache, update_wrapper
from inspect import signature
from typing import (
    Any,
    Concatenate,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    overload,
)
from weakref import ref

P = ParamSpec("P")
R = TypeVar("R")
Method = Callable[Concatenate[Any, P], R]

_CACHE_PREFIX = "_method_lru_cache_"
_DEFAULT_MAXSIZE = 128
_OWNER_ATTR = "_method_lru_cache_owner"


class _CacheInfo(Protocol):
    hits: int
    misses: int
    maxsize: int | None
    currsize: int


class _CachedMethod(Protocol[P, R]):
    __doc__: str | None
    __name__: str
    __wrapped__: Method[P, R]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def cache_clear(self) -> None: ...

    def cache_info(self) -> _CacheInfo: ...

    def cache_parameters(self) -> dict[str, Any]: ...


class _MethodLruCacheDescriptor(Generic[P, R]):
    def __init__(
        self,
        method: Method[P, R],
        maxsize: int | None,
        typed: bool = False,
    ) -> None:
        self._method = method
        self._cache_attribute = f"{_CACHE_PREFIX}{method.__name__}"
        self._maxsize = maxsize
        self._typed = typed
        # Preserve the original method metadata for class level introspection.
        update_wrapper(cast(Any, self), method)

    @property
    def maxsize(self) -> int | None:
        return self._maxsize

    @property
    def typed(self) -> bool:
        return self._typed

    def cache_parameters(self) -> dict[str, Any]:
        return {"maxsize": self._maxsize, "typed": self._typed}

    @overload
    def __get__(
        self,
        instance: None,
        owner: type[Any] | None = None,
    ) -> _MethodLruCacheDescriptor[P, R]: ...

    @overload
    def __get__(
        self,
        instance: Any,
        owner: type[Any] | None = None,
    ) -> _CachedMethod[P, R]: ...

    def __get__(
        self,
        instance: Any | None,
        owner: type[Any] | None = None,
    ) -> _MethodLruCacheDescriptor[P, R] | _CachedMethod[P, R]:
        if instance is None:
            return self

        instance_dict = self._instance_dict(instance)
        cached_method = instance_dict.get(self._cache_attribute)
        get_instance = getattr(cached_method, _OWNER_ATTR, None)
        if cached_method is None or get_instance is None or get_instance() is not instance:
            cached_method = self._create_cached_method(instance)
            try:
                instance_dict[self._cache_attribute] = cached_method
            except TypeError:
                raise TypeError(
                    f"The '__dict__' attribute on {type(instance).__name__!r} instance does "
                    f"not support item assignment for caching {self._method.__name__!r} method."
                ) from None
        return cast(_CachedMethod[P, R], cached_method)

    def _instance_dict(self, instance: Any) -> dict[str, Any]:
        try:
            instance_dict = instance.__dict__
        except AttributeError:
            raise TypeError(
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self._method.__name__!r} method."
            ) from None
        return cast(dict[str, Any], instance_dict)

    def _create_cached_method(self, instance: Any) -> _CachedMethod[P, R]:
        try:
            instance_ref = ref(instance)
        except TypeError:
            # Use a strong reference when the instance cannot be weakly referenced.
            def get_instance() -> Any:
                return instance
        else:
            get_instance = instance_ref

        @lru_cache(maxsize=self._maxsize, typed=self._typed)
        def cached_method(*args: P.args, **kwargs: P.kwargs) -> R:
            target = get_instance()
            if target is None:
                raise ReferenceError("Cached instance is no longer available")
            return self._method(target, *args, **kwargs)

        # Preserve the original method metadata on the cached callable.
        update_wrapper(cached_method, self._method)
        method_signature = signature(self._method)
        method_signature_parameters = tuple(method_signature.parameters.values())
        cached_method_any = cast(Any, cached_method)
        # Override the cache wrapper signature so introspection omits self.
        cached_method_any.__signature__ = method_signature.replace(
            parameters=method_signature_parameters[1:],
        )
        setattr(cached_method, _OWNER_ATTR, get_instance)
        return cast(_CachedMethod[P, R], cached_method)


@overload
def method_lru_cache(
    maxsize: int | None = _DEFAULT_MAXSIZE,
    typed: bool = False,
) -> Callable[[Method[P, R]], _MethodLruCacheDescriptor[P, R]]: ...


@overload
def method_lru_cache(
    maxsize: Method[P, R],
    typed: bool = False,
) -> _MethodLruCacheDescriptor[P, R]: ...


def method_lru_cache(
    maxsize: Method[P, R] | int | None = _DEFAULT_MAXSIZE,
    typed: bool = False,
) -> _MethodLruCacheDescriptor[P, R] | Callable[[Method[P, R]], _MethodLruCacheDescriptor[P, R]]:
    """Per instance LRU cache with the same calling convention as `functools.lru_cache`.

    Directly applying `functools.lru_cache` to methods can leak memory by
    retaining `self` in cache keys. See the Python FAQ
    https://docs.python.org/3/faq/programming.html#faq-cache-method-calls.
    This is especially problematic for cached arguments and fields which
    reference large networks of objects like ModelXbrl.

    This wrapper lives on the instance, so `self` is never hashed and the cache
    is collected with the instance. Bound methods expose `cache_info`,
    `cache_clear`, `cache_parameters`, and `__wrapped__`.
    """
    cache_maxsize: int | None
    if isinstance(maxsize, int):
        cache_maxsize = 0 if maxsize < 0 else maxsize
    elif callable(maxsize) and isinstance(typed, bool):
        return _MethodLruCacheDescriptor(maxsize, _DEFAULT_MAXSIZE, typed)
    elif maxsize is not None:
        raise TypeError("Expected first argument to be an integer, a callable, or None")
    else:
        cache_maxsize = None

    def decorating_function(method: Method[P, R]) -> _MethodLruCacheDescriptor[P, R]:
        return _MethodLruCacheDescriptor(method, cache_maxsize, typed)

    return decorating_function
