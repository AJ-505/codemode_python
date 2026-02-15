"""Unit checks for MCP adapter utilities."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.mcp_adapter import (
    mcp_tools_to_anthropic_schemas,
    mcp_tools_to_code_mode_api,
)


def test_mcp_conversion_shapes():
    mcp_tools = [
        {
            "name": "search-web",
            "description": "Search the web",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["query"],
            },
        }
    ]

    schemas = mcp_tools_to_anthropic_schemas(mcp_tools)
    assert len(schemas) == 1
    assert schemas[0]["name"] == "search_web"
    assert schemas[0]["input_schema"]["required"] == ["query"]

    api_text = mcp_tools_to_code_mode_api(mcp_tools)
    assert "def search_web(self, query: str, limit: Optional[int] = None) -> str:" in api_text


if __name__ == "__main__":
    test_mcp_conversion_shapes()
    print("MCP adapter tests passed")
