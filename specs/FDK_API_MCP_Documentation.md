# SBB FDK API Integration & MCP Server Konzept

## Übersicht

Diese Dokumentation fasst die wichtigsten Erkenntnisse zur SBB FDK API Integration zusammen und beschreibt ein Konzept für einen MCP (Model Context Protocol) Server zur Bereitstellung von FDK-Daten.

## SBB FDK API

### API Basis-Informationen
- **Base URL**: https://bim-fdk-api.app.sbb.ch
- **Sprache**: Deutsch (de), weitere Sprachen verfügbar
- **Format**: JSON REST API
- **Authentifizierung**: Keine (öffentliche API)

### Datenstruktur

#### FDK Object Structure
```json
{
  "id": "OBJ_BR_1",
  "name": "Brücke Standard",
  "domain": "Infrastrukturbau",
  "aksCode": "AKS_123",
  "description": "Beschreibung des Objekts",
  "summary": "Kurze Zusammenfassung",
  "homepageUrl": "https://example.com",
  "propertySets": [
    {
      "name": "Pset_Common",
      "properties": {
        "Material": {
          "value": "Beton",
          "description": "Hauptmaterial",
          "unit": "",
          "dataType": "string"
        }
      }
    }
  ],
  "properties": {
    "GlobalId": "unique-identifier",
    "Name": "Object Name"
  },
  "ifcAssignments": [
    {
      "version": "IFC4",
      "ifcClass": "IfcBridge",
      "description": "IFC Klassenzuordnung"
    }
  ]
}
```

### API Endpoints

#### Objekt abrufen
```
GET /objects/{objectId}?language=de
```

#### Objekt-ID Extraktion
Pattern für Dateinamen: `OBJ_{Domain}_{Number}_{Details}.extension`
- Beispiel: `OBJ_BR_1_Ansicht.png` → Object ID: `OBJ_BR_1`

## Implementierte Features

### Caching System
- **TTL-basiert**: Standard 3600 Sekunden (1 Stunde)
- **Thread-safe**: Verwendung von Locks für Concurrent Access
- **Automatische Bereinigung**: Expired Entries werden entfernt
- **Connection Pooling**: Session mit Retry-Mechanismus

### Performance Optimierungen
- **Async Loading**: Non-blocking API Calls
- **Debouncing**: 300ms Delay für API Requests
- **Connection Pooling**: 10 Connections, 20 Max Pool Size
- **Retry Strategy**: 3 Versuche mit Backoff

### UI Integration
- **Resizable Panel**: PanedWindow mit Sash-Position Speicherung
- **Collapsible Tree**: TreeView für Properties und Property Sets
- **Smart Click**: Explorer oder API Load basierend auf Panel-Status
- **Feature Toggle**: Ein/Aus-Schalter für API Funktionalität

## MCP Server Konzept

### Warum MCP Server?

Ein MCP Server für FDK APIs würde folgende Vorteile bieten:

1. **Standardisierte Schnittstelle**: Einheitliche Nutzung verschiedener FDK APIs
2. **Wiederverwendbarkeit**: Ein Server für multiple Projekte
3. **Skalierbarkeit**: Zentrale Verwaltung von API-Zugriffen
4. **Caching**: Shared Cache zwischen verschiedenen Clients
5. **Rate Limiting**: Schutz vor API-Überlastung

### Server Architektur

#### Tools Definition
```python
# MCP Tools für FDK Server
TOOLS = [
    {
        "name": "get_fdk_object",
        "description": "Retrieve FDK object by ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_id": {"type": "string"},
                "language": {"type": "string", "default": "de"}
            }
        }
    },
    {
        "name": "search_fdk_objects",
        "description": "Search for FDK objects by criteria",
        "inputSchema": {
            "type": "object", 
            "properties": {
                "domain": {"type": "string"},
                "name_pattern": {"type": "string"},
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "extract_object_id",
        "description": "Extract FDK object ID from filename",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"}
            }
        }
    }
]
```

#### Multi-FDK Support
```python
class FDKProvider:
    """Base class for FDK providers"""
    
    def __init__(self, base_url: str, name: str):
        self.base_url = base_url
        self.name = name
    
    async def get_object(self, object_id: str, language: str = "de"):
        """Get object from this FDK provider"""
        pass
    
    def extract_object_id(self, filename: str) -> str | None:
        """Extract object ID from filename for this provider"""
        pass

class SBBFDKProvider(FDKProvider):
    """SBB FDK specific implementation"""
    
    def __init__(self):
        super().__init__("https://bim-fdk-api.app.sbb.ch", "SBB")
    
    def extract_object_id(self, filename: str) -> str | None:
        # Implementation für SBB Pattern: OBJ_BR_1
        pass

class GenericFDKProvider(FDKProvider):
    """Generic FDK implementation for other providers"""
    pass
```

#### Server Implementation
```python
from mcp.server import Server
import asyncio

class FDKMCPServer:
    def __init__(self):
        self.server = Server("fdk-api-server")
        self.providers = {
            "sbb": SBBFDKProvider(),
            # Weitere Provider können hier hinzugefügt werden
        }
        self.cache = FDKCache()
        
    async def handle_get_fdk_object(self, object_id: str, language: str = "de", provider: str = "sbb"):
        """Handle get_fdk_object tool call"""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
            
        return await self.providers[provider].get_object(object_id, language)
    
    async def handle_search_fdk_objects(self, **criteria):
        """Handle search across all providers"""
        results = []
        for provider_name, provider in self.providers.items():
            provider_results = await provider.search(**criteria)
            for result in provider_results:
                result["provider"] = provider_name
            results.extend(provider_results)
        return results

    def run(self):
        # Register tools with MCP server
        self.server.list_tools = lambda: TOOLS
        self.server.call_tool = self._dispatch_tool_call
        
        # Start server
        asyncio.run(self.server.run())
```

### Erweiterte Features

#### Configuration Management
```python
@dataclass
class FDKServerConfig:
    providers: dict[str, dict] = field(default_factory=dict)
    cache_ttl: int = 3600
    rate_limit: int = 100  # requests per minute
    default_language: str = "de"
    log_level: str = "INFO"
```

#### Rate Limiting & Monitoring
```python
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    async def acquire(self, client_id: str):
        """Check if request is allowed"""
        pass

class FDKMetrics:
    def __init__(self):
        self.request_count = 0
        self.cache_hits = 0
        self.errors = 0
    
    def record_request(self):
        self.request_count += 1
    
    def record_cache_hit(self):
        self.cache_hits += 1
```

### Deployment & Usage

#### Installation
```bash
pip install mcp-fdk-server
```

#### Server Start
```bash
fdk-mcp-server --config fdk-config.json --port 8080
```

#### Client Usage
```python
from mcp.client import Client

client = Client("fdk-api-server")

# Get FDK object
result = await client.call_tool("get_fdk_object", {
    "object_id": "OBJ_BR_1",
    "language": "de"
})

# Extract object ID from filename  
object_id = await client.call_tool("extract_object_id", {
    "filename": "OBJ_BR_1_Ansicht.png"
})
```

## Weitere FDK Provider Integration

### Beispiel für andere FDK APIs
```python
class CustomFDKProvider(FDKProvider):
    """Custom FDK provider for organization-specific APIs"""
    
    def __init__(self, config: dict):
        super().__init__(config["base_url"], config["name"])
        self.api_key = config.get("api_key")
        self.auth_header = config.get("auth_header", "Authorization")
    
    async def get_object(self, object_id: str, language: str = "de"):
        headers = {}
        if self.api_key:
            headers[self.auth_header] = f"Bearer {self.api_key}"
        
        # Custom API implementation
        pass
    
    def extract_object_id(self, filename: str) -> str | None:
        # Custom pattern matching
        # Beispiel: "CUSTOM_OBJ_123_view.jpg" → "CUSTOM_OBJ_123"  
        pass
```

## Vorteile des MCP Ansatzes

1. **Standardisierung**: Einheitliche Schnittstelle für verschiedene FDK APIs
2. **Flexibilität**: Einfache Integration neuer FDK Provider
3. **Performance**: Zentrales Caching und Connection Pooling
4. **Sicherheit**: Zentrale Authentifizierung und Rate Limiting
5. **Monitoring**: Zentrales Logging und Metriken
6. **Wiederverwendbarkeit**: Ein Server für multiple Clients/Projekte

## Nächste Schritte

1. **Prototyp entwickeln**: Basis MCP Server mit SBB FDK Support
2. **Provider Interface definieren**: Abstraction für verschiedene FDK APIs
3. **Configuration System**: Flexible Konfiguration für verschiedene Provider
4. **Testing**: Umfassende Tests mit verschiedenen FDK APIs
5. **Documentation**: Detaillierte API-Dokumentation für Server und Clients
6. **Deployment**: Container-ready Deployment mit Docker/Kubernetes

Diese Architektur ermöglicht es, die bewährten Patterns aus der aktuellen Implementierung zu nutzen und gleichzeitig eine skalierbare, wiederverwendbare Lösung für FDK API Integration zu schaffen.