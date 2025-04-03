from typing import Protocol, Callable, Any, Dict


class IMcpFDKGateway(Protocol):
    def add_tool(self, route: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator zur Registrierung eines Tool-Handlers."""
        ...

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator zur Registrierung eines standardmäßigen Tool-Handlers (ohne explizite Route)."""
        ...

    def resource(self, route: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator zur Registrierung eines Resource-Handlers."""
        ...


class McpFDKGateway(IMcpFDKGateway):
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}
        self.resources: Dict[str, Callable[..., Any]] = {}

    def add_tool(self, route: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[route] = func
            return func
        return decorator

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Falls keine explizite Route übergeben wird, verwenden wir den Funktionsnamen.
            self.tools[func.__name__] = func
            return func
        return decorator

    def resource(self, route: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.resources[route] = func
            return func
        return decorator
