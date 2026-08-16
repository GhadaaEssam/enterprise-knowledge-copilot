from typing import TYPE_CHECKING

__all__ = ["IndexBuilder", "IndexBuildResult"]

if TYPE_CHECKING:
    from .index_builder import IndexBuilder, IndexBuildResult


def __getattr__(name: str):
    if name in __all__:
        from .index_builder import IndexBuilder, IndexBuildResult

        return {"IndexBuilder": IndexBuilder, "IndexBuildResult": IndexBuildResult}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
