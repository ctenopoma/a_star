"""a_star

Rust-backed Python package scaffold that re-exports functions from the native extension module.

Build the extension before importing in documentation or runtime contexts:
`uv run maturin develop`.
"""

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any

__all__ = ["validate_name", "__version__"]

_NATIVE_MODULE = "a_star._native"


def _load_native() -> Any:
    try:
        return import_module(_NATIVE_MODULE)
    except ImportError:
        return None


def _require_native() -> Any:
    native = _load_native()
    if native is None:
        raise RuntimeError(
            "Native extension module is not built. Run `uv run maturin develop` and retry."
        )
    return native


try:
    __version__ = version("a_star")
except PackageNotFoundError:  # pragma: no cover - fallback for editable installs
    __version__ = "0.1.0"



def validate_name(name: str) -> str:
    """Return the stripped name or raise ``ValueError`` when blank."""

    native = _require_native()
    return str(native.validate_name(str(name)))
