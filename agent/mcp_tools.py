"""Connect to FastMCP and turn its tools into async LangChain tools."""

from typing import Any
from urllib.parse import urlparse

from fastmcp import Client
from fastmcp.client.auth import OAuth
from langchain_core.tools import StructuredTool
from pydantic import Field, create_model


def python_type(field: dict[str, Any]) -> Any:
    """Convert the MCP JSON type to the matching Python type."""
    kind = field.get("type", "string")
    if kind == "integer":
        return int
    if kind == "number":
        return float
    if kind == "boolean":
        return bool
    if kind == "array":
        return list[python_type(field.get("items", {}))]
    if kind == "object":
        return dict[str, Any]
    return str


def make_tool(server_tool, url: str, auth) -> StructuredTool:
    """Make one LangChain tool that calls the matching MCP tool."""
    schema = getattr(server_tool, "input_schema", None)
    if schema is None:  # Older MCP SDKs use this spelling.
        schema = server_tool.inputSchema

    required = set(schema.get("required", []))
    fields = {}
    for name, details in schema.get("properties", {}).items():
        default = ... if name in required else None
        fields[name] = (
            python_type(details),
            Field(default, description=details.get("description", "")),
        )

    args = create_model(f"{server_tool.name.title()}Args", **fields)

    async def call_server(**arguments) -> str:
        async with Client(url, auth=auth) as client:
            result = await client.call_tool(server_tool.name, arguments)
        if result.data is not None:
            return str(result.data)
        return "\n".join(
            item.text for item in result.content if getattr(item, "text", None)
        )

    return StructuredTool(
        name=server_tool.name,
        description=server_tool.description or server_tool.name,
        args_schema=args,
        coroutine=call_server,
    )


async def load_mcp_tools(url: str, key: str | None = None) -> list[StructuredTool]:
    """List the server tools and wrap them for the LangGraph agent."""
    host = urlparse(url).hostname or ""
    if key:
        auth = key
    elif host.endswith((".fastmcp.app", ".horizon.prefect.io")):
        # Horizon uses browser-based OAuth. Reuse this OAuth object so its
        # token can be reused by the tool wrappers after tool discovery.
        auth = OAuth()
    else:
        auth = None

    async with Client(url, auth=auth) as client:
        server_tools = await client.list_tools()
    return [make_tool(tool, url, auth) for tool in server_tools]
