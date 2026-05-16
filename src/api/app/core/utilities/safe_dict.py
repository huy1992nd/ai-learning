from typing import Generic, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class SafeDict(dict[K, V], Generic[K, V]):
    def __init__(self, *args, fallback_key: K | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fallback_key = fallback_key

    def __missing__(self, key):
        if self.fallback_key is not None:
            return self[self.fallback_key]

        first_key = next(iter(self))
        return self[first_key]