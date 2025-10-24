"""Dependency Injection infrastructure.

This module provides the DI container and plugin registry for managing
application dependencies following Clean Architecture principles.

Key Components:
- Container: Dependency Injection container that wires components together
- PluginRegistry: Registry for managing FDK plugin instances

Example:
    ```python
    from fdk_mcp.infrastructure import Container
    from fdk_mcp.use_cases import ListObjectsUseCase

    # Initialize container
    container = Container()

    # Get use case with injected dependencies
    use_case = container.get_use_case(ListObjectsUseCase)

    # Execute use case
    response = await use_case.execute(request)
    ```
"""

from .container import Container
from .plugin_registry import PluginRegistry


__all__ = [
    "Container",
    "PluginRegistry",
]
