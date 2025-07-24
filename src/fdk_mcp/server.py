"""
FDK MCP Server - Main server implementation
"""

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

from .data_provider import FDKDataProvider
from .models import FDKSearchCriteria, FDKServerConfig


class FDKMCPServer:
    """MCP Server for FDK (Fach-Daten-Katalog) data access"""

    def __init__(self, config: FDKServerConfig):
        self.config = config
        self.server = Server("fdk-server")
        self.data_provider = FDKDataProvider(config)
        self.logger = logging.getLogger(__name__)

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Register handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP message handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_fdk_object",
                        description="Retrieve a specific FDK object by its ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "object_id": {
                                    "type": "string",
                                    "description": "The FDK object ID (e.g., 'OBJ_FB_1', 'OBJ_BR_1')",
                                }
                            },
                            "required": ["object_id"],
                        },
                    ),
                    Tool(
                        name="search_fdk_objects",
                        description="Search for FDK objects based on various criteria",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name_pattern": {
                                    "type": "string",
                                    "description": "Search pattern for object names (case insensitive)",
                                },
                                "domain": {
                                    "type": "string",
                                    "description": "Filter by domain (e.g., 'Fahrbahn', 'Hochbau', 'Brückenbau')",
                                },
                                "object_type": {
                                    "type": "string",
                                    "description": "Filter by object type (e.g., 'FB', 'BR', 'HB', 'EN')",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return (default: 10)",
                                    "default": 10,
                                },
                            },
                        },
                    ),
                    Tool(
                        name="extract_object_id",
                        description="Extract FDK object ID from a filename",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "Filename to extract object ID from (e.g., 'OBJ_BR_1_Ansicht.png')",
                                }
                            },
                            "required": ["filename"],
                        },
                    ),
                    Tool(
                        name="analyze_references",
                        description="Analyze reference relationships for a specific FDK object",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "object_id": {
                                    "type": "string",
                                    "description": "The FDK object ID to analyze",
                                },
                                "max_depth": {
                                    "type": "integer",
                                    "description": "Maximum depth for reference analysis (default: 3)",
                                    "default": 3,
                                },
                            },
                            "required": ["object_id"],
                        },
                    ),
                    Tool(
                        name="get_reference_network",
                        description="Get a network of reference relationships starting from an object",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "start_object_id": {
                                    "type": "string",
                                    "description": "The starting FDK object ID for network analysis",
                                },
                                "max_depth": {
                                    "type": "integer",
                                    "description": "Maximum depth for network analysis (default: 2)",
                                    "default": 2,
                                },
                            },
                            "required": ["start_object_id"],
                        },
                    ),
                    Tool(
                        name="get_domains",
                        description="Get all available FDK domains",
                        inputSchema={"type": "object", "properties": {}},
                    ),
                    Tool(
                        name="get_object_types",
                        description="Get all available FDK object types",
                        inputSchema={"type": "object", "properties": {}},
                    ),
                    Tool(
                        name="get_all_objects",
                        description="Get all loaded FDK objects (use with caution - can be large)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "summary_only": {
                                    "type": "boolean",
                                    "description": "Return only ID and name for each object (default: true)",
                                    "default": True,
                                }
                            },
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any]
        ) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "get_fdk_object":
                    return await self._handle_get_fdk_object(arguments)
                elif name == "search_fdk_objects":
                    return await self._handle_search_fdk_objects(arguments)
                elif name == "extract_object_id":
                    return await self._handle_extract_object_id(arguments)
                elif name == "analyze_references":
                    return await self._handle_analyze_references(arguments)
                elif name == "get_reference_network":
                    return await self._handle_get_reference_network(arguments)
                elif name == "get_domains":
                    return await self._handle_get_domains(arguments)
                elif name == "get_object_types":
                    return await self._handle_get_object_types(arguments)
                elif name == "get_all_objects":
                    return await self._handle_get_all_objects(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                self.logger.error(f"Error handling tool call {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {e!s}")]
                )

    async def _handle_get_fdk_object(self, arguments: dict[str, Any]) -> CallToolResult:
        """Handle get_fdk_object tool call"""
        object_id = arguments.get("object_id", "").strip()
        if not object_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: object_id is required")]
            )

        fdk_object = await self.data_provider.get_object(object_id)
        if not fdk_object:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Object not found: {object_id}")
                ]
            )

        result = {
            "id": fdk_object.id,
            "name": fdk_object.name,
            "domain": fdk_object.domain_name,
            "description": fdk_object.get_plain_description(),
            "object_type": fdk_object.object_type,
            "component_relationships": [
                {"id": rel.id, "name": rel.name}
                for rel in fdk_object.component_relationships
            ],
            "assembly_relationships": [
                {"id": rel.id, "name": rel.name}
                for rel in fdk_object.assembly_relationships
            ],
        }

        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]
        )

    async def _handle_search_fdk_objects(
        self, arguments: dict[str, Any]
    ) -> CallToolResult:
        """Handle search_fdk_objects tool call"""
        criteria = FDKSearchCriteria(
            name_pattern=arguments.get("name_pattern"),
            domain=arguments.get("domain"),
            object_type=arguments.get("object_type"),
            limit=arguments.get("limit", 10),
        )

        search_result = await self.data_provider.search_objects(criteria)

        result = {
            "total_count": search_result.total_count,
            "objects": [
                {
                    "id": obj.id,
                    "name": obj.name,
                    "domain": obj.domain_name,
                    "object_type": obj.object_type,
                    "description": obj.description[:200] + "..."
                    if len(obj.description) > 200
                    else obj.description,
                }
                for obj in search_result.objects
            ],
        }

        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]
        )

    async def _handle_extract_object_id(
        self, arguments: dict[str, Any]
    ) -> CallToolResult:
        """Handle extract_object_id tool call"""
        filename = arguments.get("filename", "").strip()
        if not filename:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: filename is required")]
            )

        object_id = self.data_provider.extract_object_id_from_filename(filename)

        result = {
            "filename": filename,
            "extracted_object_id": object_id,
            "success": object_id is not None,
        }

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )

    async def _handle_analyze_references(
        self, arguments: dict[str, Any]
    ) -> CallToolResult:
        """Handle analyze_references tool call"""
        object_id = arguments.get("object_id", "").strip()
        max_depth = arguments.get("max_depth", 3)

        if not object_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: object_id is required")]
            )

        analysis = await self.data_provider.analyze_references(object_id, max_depth)

        result = {
            "object_id": analysis.object_id,
            "referenced_by": analysis.referenced_by,
            "references_to": analysis.references_to,
            "reference_count": analysis.reference_count,
            "depth_level": analysis.depth_level,
        }

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )

    async def _handle_get_reference_network(
        self, arguments: dict[str, Any]
    ) -> CallToolResult:
        """Handle get_reference_network tool call"""
        start_object_id = arguments.get("start_object_id", "").strip()
        max_depth = arguments.get("max_depth", 2)

        if not start_object_id:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="Error: start_object_id is required")
                ]
            )

        network = await self.data_provider.get_reference_network(
            start_object_id, max_depth
        )

        result = {
            "start_object_id": start_object_id,
            "max_depth": max_depth,
            "network": {
                obj_id: {
                    "referenced_by": analysis.referenced_by,
                    "references_to": analysis.references_to,
                    "reference_count": analysis.reference_count,
                    "depth_level": analysis.depth_level,
                }
                for obj_id, analysis in network.items()
            },
        }

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )

    async def _handle_get_domains(self, arguments: dict[str, Any]) -> CallToolResult:
        """Handle get_domains tool call"""
        domains = await self.data_provider.get_domains()

        result = {"domains": domains, "count": len(domains)}

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )

    async def _handle_get_object_types(
        self, arguments: dict[str, Any]
    ) -> CallToolResult:
        """Handle get_object_types tool call"""
        object_types = await self.data_provider.get_object_types()

        result = {"object_types": object_types, "count": len(object_types)}

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )

    async def _handle_get_all_objects(
        self, arguments: dict[str, Any]
    ) -> CallToolResult:
        """Handle get_all_objects tool call"""
        summary_only = arguments.get("summary_only", True)
        all_objects = await self.data_provider.get_all_objects()

        if summary_only:
            result = {
                "total_count": len(all_objects),
                "objects": [
                    {
                        "id": obj.id,
                        "name": obj.name,
                        "domain": obj.domain_name,
                        "object_type": obj.object_type,
                    }
                    for obj in all_objects
                ],
            }
        else:
            result = {
                "total_count": len(all_objects),
                "objects": [obj.model_dump() for obj in all_objects],
            }

        return CallToolResult(
            content=[
                TextContent(
                    type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]
        )

    async def run(self) -> None:
        """Run the MCP server"""
        self.logger.info("Starting FDK MCP Server...")
        await self.data_provider.initialize()
        self.logger.info("FDK MCP Server initialized and ready")

    async def cleanup(self) -> None:
        """Cleanup resources"""
        await self.data_provider.close()
        self.logger.info("FDK MCP Server shutdown complete")
