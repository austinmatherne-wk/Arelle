"""
See COPYRIGHT.md for copyright information.
"""

from __future__ import annotations

import copy
import gc
import inspect
import weakref
from functools import lru_cache
from typing import Any

import pytest

from arelle.utils.MethodLruCache import method_lru_cache


class CacheExample:
    __hash__ = None

    def __init__(self, name: str) -> None:
        self.name = name
        self.calls = 0

    @method_lru_cache
    def cached(self, key: str) -> tuple[str, str, int]:
        """Return a cached tuple for *key*."""
        self.calls += 1
        return self.name, key, self.calls

    @method_lru_cache
    def another(self) -> int:
        self.calls += 1
        return self.calls


class ConfigurableCacheExample:
    def __init__(self) -> None:
        self.calls = 0

    @method_lru_cache(2)
    def cached(self, key: int) -> int:
        self.calls += 1
        return self.calls


class TypedCacheExample:
    def __init__(self) -> None:
        self.calls = 0

    @method_lru_cache(maxsize=10, typed=True)
    def cached(self, key: int | float) -> int:
        self.calls += 1
        return self.calls


class PositionalTypedCacheExample:
    def __init__(self) -> None:
        self.calls = 0

    @method_lru_cache(10, True)
    def cached(self, key: int | float) -> int:
        self.calls += 1
        return self.calls


class NonWeakrefableCacheExample:
    __slots__ = ("__dict__",)

    def __init__(self) -> None:
        self.calls = 0

    @method_lru_cache
    def cached(self) -> int:
        self.calls += 1
        return self.calls


class SlottedCacheExample:
    __slots__ = ("calls",)

    def __init__(self) -> None:
        self.calls = 0

    @method_lru_cache
    def cached(self) -> int:
        self.calls += 1
        return self.calls


def _make_cache_behavior_example(decorator: Any) -> type[Any]:
    class CacheBehaviorExample:
        def __init__(self) -> None:
            self.calls = 0

        @decorator(maxsize=2, typed=True)
        def cached(
            self,
            key: int | float,
            *,
            label: str = "",
        ) -> tuple[int | float, str, int]:
            self.calls += 1
            return key, label, self.calls

    return CacheBehaviorExample


def _run_cache_behavior(instance: Any) -> tuple[Any, ...]:
    first = instance.cached(1, label="one")
    repeated = instance.cached(1, label="one")
    typed = instance.cached(1.0, label="one")
    keyword = instance.cached(key=1, label="one")
    after_eviction = instance.cached(1, label="one")
    cache_info_before_clear = instance.cached.cache_info()
    instance.cached.cache_clear()
    cache_info_after_clear = instance.cached.cache_info()
    after_clear = instance.cached(2, label="two")
    return (
        first,
        repeated,
        typed,
        keyword,
        after_eviction,
        after_clear,
        instance.calls,
        cache_info_before_clear,
        cache_info_after_clear,
        instance.cached.cache_parameters(),
        inspect.signature(instance.cached),
    )


def test_method_lru_cache_matches_lru_cache_behavior() -> None:
    method_cache_instance = _make_cache_behavior_example(method_lru_cache)()
    lru_cache_instance = _make_cache_behavior_example(lru_cache)()

    method_cache_behavior = _run_cache_behavior(method_cache_instance)
    lru_cache_behavior = _run_cache_behavior(lru_cache_instance)

    assert method_cache_behavior == lru_cache_behavior


def test_cache_hits_and_misses_are_based_on_arguments() -> None:
    instance = CacheExample("example")

    first = instance.cached("first")
    assert instance.cached("first") is first
    assert instance.cached("second") != first
    assert instance.calls == 2
    assert instance.cached.cache_info().hits == 1
    assert instance.cached.cache_info().misses == 2


def test_default_cache_size_matches_lru_cache() -> None:
    instance = CacheExample("example")

    instance.cached("first")
    instance.cached("second")

    cache_info = instance.cached.cache_info()
    assert cache_info.maxsize == 128
    assert cache_info.currsize == 2


def test_configured_cache_size_is_forwarded() -> None:
    instance = ConfigurableCacheExample()

    assert instance.cached(1) == 1
    assert instance.cached(2) == 2
    assert instance.cached(1) == 1
    assert instance.cached(3) == 3
    assert instance.cached.cache_info().maxsize == 2
    assert instance.cached.cache_info().hits == 1
    assert instance.cached.cache_info().misses == 3


def test_cache_parameters_are_exposed_on_bound_method() -> None:
    instance = ConfigurableCacheExample()

    assert instance.cached.cache_parameters() == {"maxsize": 2, "typed": False}


def test_cache_parameters_and_attributes_are_exposed_on_descriptor() -> None:
    assert CacheExample.cached.maxsize == 128
    assert CacheExample.cached.typed is False
    assert CacheExample.cached.cache_parameters() == {
        "maxsize": 128,
        "typed": False,
    }

    assert ConfigurableCacheExample.cached.maxsize == 2
    assert ConfigurableCacheExample.cached.typed is False
    assert ConfigurableCacheExample.cached.cache_parameters() == {
        "maxsize": 2,
        "typed": False,
    }

    assert TypedCacheExample.cached.maxsize == 10
    assert TypedCacheExample.cached.typed is True
    assert TypedCacheExample.cached.cache_parameters() == {
        "maxsize": 10,
        "typed": True,
    }

    assert PositionalTypedCacheExample.cached.maxsize == 10
    assert PositionalTypedCacheExample.cached.typed is True
    assert PositionalTypedCacheExample.cached.cache_parameters() == {"maxsize": 10, "typed": True}


def test_typed_cache_distinguishes_types() -> None:
    instance = TypedCacheExample()

    assert instance.cached(1) == 1
    assert instance.cached(1.0) == 2
    assert instance.cached(1) == 1
    assert instance.calls == 2
    assert instance.cached.cache_info().hits == 1
    assert instance.cached.cache_info().misses == 2


def test_positional_typed_cache_distinguishes_types() -> None:
    instance = PositionalTypedCacheExample()

    assert instance.cached(1) == 1
    assert instance.cached(1.0) == 2
    assert instance.cached(1) == 1
    assert instance.calls == 2


def test_method_lru_cache_rejects_invalid_maxsize() -> None:
    with pytest.raises(TypeError, match="integer"):
        method_lru_cache("nope")  # type: ignore[arg-type]


def test_cache_is_isolated_between_instances() -> None:
    first_instance = CacheExample("first")
    second_instance = CacheExample("second")

    first_value = first_instance.cached("key")
    second_value = second_instance.cached("key")

    assert first_value != second_value
    assert first_instance.calls == 1
    assert second_instance.calls == 1


def test_copied_instance_does_not_reuse_original_cache() -> None:
    instance = CacheExample("example")
    instance.cached("key")
    copied = copy.copy(instance)

    assert copied.cached("key") == ("example", "key", 2)
    assert copied.calls == 2
    assert instance.calls == 1
    assert instance.cached("key") == ("example", "key", 1)


def test_unhashable_instances_can_use_cached_methods() -> None:
    instance = CacheExample("example")

    with pytest.raises(TypeError):
        hash(instance)

    assert instance.cached("key") is instance.cached("key")
    assert instance.calls == 1


def test_bound_cache_exposes_method_metadata() -> None:
    instance = CacheExample("example")

    assert instance.cached.__name__ == "cached"
    assert instance.cached.__doc__ == "Return a cached tuple for *key*."
    assert CacheExample.cached.__doc__ == "Return a cached tuple for *key*."
    assert instance.cached.__wrapped__ is CacheExample.cached.__wrapped__


def test_bound_cache_signature_omits_self() -> None:
    instance = CacheExample("example")

    assert list(inspect.signature(instance.cached).parameters) == ["key"]
    assert list(inspect.signature(instance.another).parameters) == []


def test_bound_cache_clear_invalidates_one_method() -> None:
    instance = CacheExample("example")

    instance.cached("key")
    instance.another()
    instance.cached.cache_clear()
    instance.cached("key")

    assert instance.calls == 3
    assert instance.cached.cache_info().currsize == 1
    assert instance.another.cache_info().currsize == 1


def test_cached_instance_can_be_collected() -> None:
    def get_instance_reference() -> weakref.ReferenceType[CacheExample]:
        instance = CacheExample("example")
        instance.cached("key")
        return weakref.ref(instance)

    instance_reference = get_instance_reference()
    gc.collect()

    assert instance_reference() is None


def test_non_weakrefable_instance_uses_direct_closure() -> None:
    instance = NonWeakrefableCacheExample()

    with pytest.raises(TypeError):
        weakref.ref(instance)

    assert instance.cached() == 1
    assert instance.cached() == 1
    assert instance.calls == 1


def test_non_weakrefable_instance_can_be_collected() -> None:
    class Token:
        pass

    def get_token_reference() -> weakref.ReferenceType[Token]:
        token = Token()
        instance = NonWeakrefableCacheExample()
        instance.token = token
        instance.cached()
        return weakref.ref(token)

    token_reference = get_token_reference()
    gc.collect()

    assert token_reference() is None


def test_slotted_instance_without_dict_raises_type_error() -> None:
    instance = SlottedCacheExample()

    with pytest.raises(TypeError, match="__dict__"):
        instance.cached()
