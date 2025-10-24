"""Infrastructure layer - framework and external dependencies.

This module provides concrete implementations of domain abstractions
and the dependency injection infrastructure.

Key Components:
- Container: DI container for wiring dependencies
- PluginRegistry: Registry for managing FDK plugins
- FileCacheRepository: File-based cache implementation

Example:
    ```python
    from fdk_mcp.infrastructure import Container
    from fdk_mcp.use_cases import ListObjectsUseCase

    # Initialize application
    container = Container()

    # Get use case with injected dependencies
    use_case = container.get_use_case(ListObjectsUseCase)
    ```
"""

from .cache import FileCacheRepository
from .di import Container, PluginRegistry


__all__ = [
    # Dependency Injection
    "Container",
    "PluginRegistry",
    # Cache Implementation
    "FileCacheRepository",
]
