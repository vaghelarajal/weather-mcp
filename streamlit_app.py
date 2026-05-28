"""Minimalist Streamlit UI for the Weather MCP project.

This file is a visual MCP Client.
It talks to the MCP Server by calling MCP tools.
"""

import asyncio
import json
import sys
from datetime import datetime
from html import escape

import streamlit as st
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def read_tool_json(tool_result):
    """Read JSON text returned by an MCP tool."""

    # MCP tool results contain content blocks.
    # Our weather server returns one text block containing JSON.
    text_content = tool_result.content[0].text

    # Convert JSON text into a Python dictionary.
    return json.loads(text_content)


async def call_get_weather_tool(city: str):
    """Call the get_weather tool on the MCP Server."""

    print(f"Streamlit UI: Calling get_weather tool for {city}.")

    # This tells Streamlit how to start the MCP Server.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["weather_server.py"],
    )

    # Open a stdio connection to the MCP Server.
    async with stdio_client(server_params) as (read_stream, write_stream):
        # Create an MCP session using the read/write streams.
        async with ClientSession(read_stream, write_stream) as session:
            # MCP clients always initialize before calling tools.
            await session.initialize()

            # Call the real MCP tool named get_weather.
            tool_result = await session.call_tool(
                "get_weather",
                arguments={"city": city},
            )

            return read_tool_json(tool_result)


def build_ai_style_message(weather_result: dict):
    """Create a friendly assistant-style weather message."""

    # Read the weather values returned by the MCP Server.
    location = weather_result["location"]
    temperature = weather_result["temperature"]
    condition = weather_result["condition"]

    # Use lowercase condition text inside a natural sentence.
    condition_text = condition.lower()

    # Choose a simple second sentence based on the weather condition.
    if "rain" in condition_text or "drizzle" in condition_text:
        advice = "You may want to carry an umbrella today."
    elif "snow" in condition_text:
        advice = "Bundle up before heading outside."
    elif "thunderstorm" in condition_text:
        advice = "It is better to stay safe indoors if you can."
    elif "clear" in condition_text or "sun" in condition_text:
        advice = "Perfect weather for going outside \u2600\ufe0f"
    elif "cloud" in condition_text or "overcast" in condition_text:
        advice = "A calm day with softer skies."
    elif "fog" in condition_text:
        advice = "Visibility may be low, so travel carefully."
    else:
        advice = "Have a good day and check again later if the weather changes."

    return f"{location} is currently {temperature} with {condition_text}.\n\n{advice}"


def format_forecast_date(date_text: str):
    """Convert an API date like 2026-05-28 into May 28."""

    forecast_date = datetime.strptime(date_text, "%Y-%m-%d")

    return forecast_date.strftime("%b %d")


def get_icon(icon_name: str):
    """Convert a server icon name into a visual weather icon."""

    icons = {
        "sun": "\u2600\ufe0f",
        "cloud": "\u2601\ufe0f",
        "rain": "\U0001f327\ufe0f",
        "snow": "\u2744\ufe0f",
        "storm": "\u26c8\ufe0f",
        "fog": "\U0001f32b\ufe0f",
        "mixed": "\U0001f324\ufe0f",
    }

    return icons.get(icon_name, "\U0001f324\ufe0f")


def get_app_css():
    """Return one calm ivory theme for the whole app."""

    background = "#fffdf4"
    border = "#eee7d6"
    accent = "#4f6f8f"

    return f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at top left, rgba(255, 255, 255, 0.95), transparent 34rem),
            {background};
    }}

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    header,
    footer {{
        visibility: hidden;
        height: 0;
    }}

    .block-container {{
        max-width: 860px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }}

    h1 {{
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: 0;
        margin-bottom: 0.25rem;
    }}

    h3 {{
        margin-top: 1.6rem;
        letter-spacing: 0;
    }}

    .app-subtitle {{
        color: #64748b;
        margin-bottom: 1.25rem;
    }}

    .weather-card {{
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid {border};
        border-radius: 8px;
        padding: 18px;
        margin-top: 14px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
    }}

    .hero-card {{
        display: grid;
        grid-template-columns: 86px 1fr;
        gap: 18px;
        align-items: center;
        border-top: 4px solid {accent};
    }}

    .stButton > button {{
        background: {accent};
        border-color: {accent};
        color: #ffffff;
    }}

    .stButton > button:hover {{
        background: #3f5f7a;
        border-color: #3f5f7a;
        color: #ffffff;
    }}

    .weather-icon {{
        font-size: 52px;
        line-height: 1;
    }}

    .weather-title {{
        font-size: 21px;
        font-weight: 800;
        margin-bottom: 6px;
    }}

    .weather-text {{
        color: #475569;
        line-height: 1.55;
        white-space: pre-line;
    }}

    .small-label {{
        color: #64748b;
        font-size: 13px;
        margin-bottom: 4px;
    }}

    .small-value {{
        color: #0f172a;
        font-size: 23px;
        font-weight: 800;
    }}

    .forecast-grid {{
        display: grid;
        gap: 12px;
        grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
        margin-top: 12px;
    }}

    .forecast-card {{
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid {border};
        border-radius: 8px;
        padding: 14px;
        min-height: 154px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
    }}

    .forecast-icon {{
        font-size: 30px;
        line-height: 1;
        margin-bottom: 10px;
    }}

    </style>
    """


def render_info_card(label: str, value: str):
    """Render one small minimalist card."""

    st.markdown(
        f"""
        <div class="weather-card">
            <div class="small-label">{escape(label)}</div>
            <div class="small-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_forecast_cards(forecast: list[dict]):
    """Render the 5-day forecast using native Streamlit cards."""

    # Streamlit columns render reliably in the browser.
    # This avoids raw HTML being shown as text.
    forecast_columns = st.columns(len(forecast))

    for index, day in enumerate(forecast):
        with forecast_columns[index]:
            with st.container(border=True):
                st.markdown(f"### {get_icon(day['icon'])}")
                st.caption(format_forecast_date(day["date"]))
                st.markdown(f"**{day['max_temperature']}**")
                st.caption(f"Low {day['min_temperature']}")
                st.caption(day["condition"])


# Configure the browser tab and page layout.
st.set_page_config(
    page_title="Weather MCP",
    layout="centered",
)


if "last_weather" not in st.session_state:
    st.session_state.last_weather = None


# Apply the single ivory theme.
st.markdown(get_app_css(), unsafe_allow_html=True)


# Main title shown on the page.
st.title("Weather")
st.markdown('<div class="app-subtitle">Search real weather for any city.</div>', unsafe_allow_html=True)


# The form lets the user press Enter or click the button to search.
with st.form("weather_search_form"):
    # Let the user type any city in the world.
    selected_city = st.text_input(
        "Search city",
        placeholder="Try Ahmedabad, Tokyo, London, New York...",
    )

    # Pressing Enter inside the input submits this form.
    search_submitted = st.form_submit_button(
        "Get Weather",
        use_container_width=True,
        type="primary",
    )


if search_submitted:
    # Stop early if the user clicks the button without typing a city.
    if not selected_city.strip():
        st.warning("Please enter a city name.")
        st.stop()

    # Show a spinner while waiting for the server response.
    with st.spinner("Calling get_weather tool..."):
        try:
            weather_result = asyncio.run(call_get_weather_tool(selected_city))
        except Exception:
            st.error("MCP Server could not be reached. Install dependencies with: pip install -r requirements.txt")
            st.stop()

    # If the server returns success, save it so Streamlit can render the cards.
    if weather_result["success"]:
        st.session_state.last_weather = weather_result
    else:
        # Show the error message returned by the server.
        st.warning(weather_result["message"])


if st.session_state.last_weather is not None:
    weather = st.session_state.last_weather
    safe_location = escape(weather["location"])
    safe_message = escape(build_ai_style_message(weather))

    st.markdown(
        f"""
        <div class="weather-card hero-card">
            <div class="weather-icon">{get_icon(weather["icon"])}</div>
            <div>
                <div class="weather-title">{safe_location}</div>
                <div class="weather-text">{safe_message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_card, right_card = st.columns(2)

    with left_card:
        render_info_card("Humidity", weather["humidity"])

    with right_card:
        render_info_card("Wind", weather["wind_speed"])

    st.subheader("5-day forecast")
    render_forecast_cards(weather["forecast"])
