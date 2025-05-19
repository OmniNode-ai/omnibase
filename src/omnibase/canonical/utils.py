from typing import Any

from .canonical_serialization import CanonicalYAMLSerializer


def canonicalize_metadata_block(*args: Any, **kwargs: Any) -> str:
    return CanonicalYAMLSerializer().canonicalize_metadata_block(*args, **kwargs)
