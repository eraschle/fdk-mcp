#!/usr/bin/env python3
"""
FDK MCP Server - Main entry point
"""

import asyncio
import logging
import sys

from src.fdk_mcp import FDKMCPServer, FDKServerConfig


async def main():
    """Main entry point for the FDK MCP Server"""

    # Configuration
    config = FDKServerConfig(
        data_directory="data/sample",
        api_base_url="https://bim-fdk-api.app.sbb.ch",
        api_language="de",
        cache_ttl_seconds=3600,
        enable_api_fallback=True,
        max_search_results=100,
        log_level="INFO",
    )

    # Create and run server
    server = FDKMCPServer(config)

    try:
        await server.run()
        # Keep the server running
        await server.server.run()
    except KeyboardInterrupt:
        logging.info("Shutting down FDK MCP Server...")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
