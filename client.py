"""Beginner-friendly MCP Client for the Weather MCP Server.

This file is the MCP Client.
It starts the MCP Server, discovers tools, calls get_weather, and prints the result.
"""

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def read_tool_json(tool_result):
    """Read JSON text returned by an MCP tool."""

    # MCP tool results contain content blocks.
    # Our server returns one text block containing JSON.
    text_content = tool_result.content[0].text

    # Convert the JSON text into a Python dictionary.
    return json.loads(text_content)


async def call_get_weather_tool(city: str):
    """Connect to the MCP Server and call the get_weather tool."""

    print("\nMCP Client: Starting Weather MCP Server process.")

    # This tells the client how to start the MCP Server.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["weather_server.py"],
    )

    # Open a stdio connection to the MCP Server.
    async with stdio_client(server_params) as (read_stream, write_stream):
        print("MCP Client: Connected to MCP Server over stdio.")

        # Create an MCP session using the read/write streams.
        async with ClientSession(read_stream, write_stream) as session:
            print("MCP Client: Initializing MCP session.")
            await session.initialize()

            print("MCP Client: Asking server which tools are available.")
            tools_result = await session.list_tools()
            tool_names = [tool.name for tool in tools_result.tools]
            print(f"MCP Client: Available tools: {tool_names}")

            print(f"MCP Client: Calling get_weather tool for: {city}")
            tool_result = await session.call_tool(
                "get_weather",
                arguments={"city": city},
            )

            print("MCP Client: Tool response received.")

            return read_tool_json(tool_result)


def main():
    """Run the MCP client program."""

    print("Weather MCP Client started.")
    print("You can enter any world city, such as Ahmedabad, Tokyo, London, or New York.")

    city = input("\nWhat city do you want weather for? ")

    weather_result = asyncio.run(call_get_weather_tool(city))

    print("\nMCP Client: Formatting final answer for the user.")

    if weather_result["success"]:
        print(
            f'{weather_result["location"]} is '
            f'{weather_result["temperature"]} and '
            f'{weather_result["condition"]}.'
        )
        return

    print(weather_result["message"])


if __name__ == "__main__":
    main()
