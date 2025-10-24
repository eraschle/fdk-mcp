"""Main entry point for SBB FDK MCP server."""

from fdk_mcp.server import mcp


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
