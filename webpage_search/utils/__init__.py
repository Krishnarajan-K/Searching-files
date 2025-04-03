# This makes `utils` a package, allowing imports from it.
# You can also define shared utility functions or imports here.

from .search import (
    get_text_files_content,
    improved_search_in_repo,
    safe_search,
    get_context
)

__all__ = ["get_text_files_content", "improved_search_in_repo", "safe_search", "get_context"]
