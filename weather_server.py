"""Real MCP Weather Server.

This file is the MCP Server.
It exposes MCP tools that a real MCP Client can discover and call.
"""

import json

from mcp.server.fastmcp import FastMCP

from weather_service import get_temperature_data, get_weather_data


# FastMCP creates an MCP server.
# The name is shown to MCP clients during connection.
mcp = FastMCP("Weather MCP Server")


@mcp.tool()
def get_weather(city: str) -> str:
    """Get real current weather and 5-day forecast for any city or place."""

    # The actual weather logic lives in weather_service.py.
    weather_result = get_weather_data(city)

    # Returning JSON text keeps the beginner client easy to understand.
    return json.dumps(weather_result, ensure_ascii=False)


@mcp.tool()
def get_temperature(city: str) -> str:
    """Get only the current temperature for any city or place."""

    temperature_result = get_temperature_data(city)

    return json.dumps(temperature_result, ensure_ascii=False)


if __name__ == "__main__":
    # Start the MCP server using stdio transport.
    # MCP clients communicate with this process through standard input/output.
    mcp.run()
