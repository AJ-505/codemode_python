"""
MCP compatibility helpers.

These utilities translate legacy MCP tool definitions into:
- Anthropic-style JSON schemas (for regular tool-calling mode)
- Python API docs string (for Code Mode prompts)
"""

from __future__ import annotations

import json
import keyword
import re
from pathlib import Path
from typing import Any, Dict, List


def load_mcp_tools_from_file(path: str) -> List[Dict[str, Any]]:
    """
    Load MCP tool definitions from a JSON file.

    Accepted file structures:
    - [{"name": "...", ...}, ...]
    - {"tools": [{"name": "...", ...}, ...]}
    """
    payload = json.loads(Path(path).read_text())
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("tools"), list):
        return payload["tools"]
    raise ValueError("Invalid MCP tools file format; expected list or {'tools': [...]} object")


def _sanitize_identifier(name: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z_]", "_", name)
    if not cleaned:
        cleaned = "tool"
    if cleaned[0].isdigit():
        cleaned = f"tool_{cleaned}"
    if keyword.iskeyword(cleaned):
        cleaned = f"{cleaned}_tool"
    return cleaned


def _extract_input_schema(tool: Dict[str, Any]) -> Dict[str, Any]:
    return tool.get("inputSchema") or tool.get("input_schema") or {"type": "object", "properties": {}, "required": []}


def mcp_tools_to_anthropic_schemas(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert MCP tool definitions to the schema format used by this benchmark.
    """
    converted = []
    for tool in mcp_tools:
        name = _sanitize_identifier(tool.get("name", "tool"))
        converted.append(
            {
                "name": name,
                "description": tool.get("description", ""),
                "input_schema": _extract_input_schema(tool),
            }
        )
    return converted


def _json_type_to_python(type_name: str) -> str:
    type_map = {
        "string": "str",
        "number": "float",
        "integer": "int",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
    }
    return type_map.get(type_name, "Any")


def mcp_tools_to_code_mode_api(mcp_tools: List[Dict[str, Any]]) -> str:
    """
    Build a Code-Mode API reference string from MCP tools.
    """
    lines: List[str] = [
        "from typing import Any, Dict, List, Optional",
        "",
        "# Auto-generated from MCP tool definitions",
        "class Tools:",
    ]

    for tool in mcp_tools:
        tool_name = _sanitize_identifier(tool.get("name", "tool"))
        description = tool.get("description", "No description provided.")
        input_schema = _extract_input_schema(tool)
        properties = input_schema.get("properties", {})
        required = set(input_schema.get("required", []))

        args = []
        for arg_name, arg_schema in properties.items():
            safe_arg_name = _sanitize_identifier(arg_name)
            py_type = _json_type_to_python(arg_schema.get("type", "string"))
            if arg_name in required:
                args.append(f"{safe_arg_name}: {py_type}")
            else:
                args.append(f"{safe_arg_name}: Optional[{py_type}] = None")

        signature_args = ", ".join(args)
        if signature_args:
            signature_args = f", {signature_args}"

        lines.extend(
            [
                f"    def {tool_name}(self{signature_args}) -> str:",
                '        """',
                f"        {description}",
                "",
                "        Returns:",
                "            JSON string result from the underlying MCP tool.",
                '        """',
                "        pass",
                "",
            ]
        )

    if len(lines) == 4:
        lines.extend(
            [
                "    def noop(self) -> str:",
                '        """No MCP tools were provided."""',
                "        pass",
            ]
        )

    return "\n".join(lines)
