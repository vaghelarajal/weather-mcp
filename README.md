# Weather MCP

A beginner-friendly Python project that demonstrates how an MCP Client communicates with an MCP Server to fetch real-time weather data.

## Features

* Real MCP Server using Python MCP SDK
* MCP Client using `ClientSession`
* Streamlit UI
* Real-time weather data using Open-Meteo API
* Current temperature
* Humidity and wind speed
* 5-day weather forecast
* MCP tool discovery and tool calling

---

## Architecture

```text
User
 ↓
MCP Client
 ↓
MCP Server
 ↓
get_weather Tool
 ↓
Open-Meteo API
 ↓
Weather Response
```

---

## Project Structure

```text
weather-mcp/
│
├── weather_server.py      # MCP Server with weather tools
├── client.py              # Terminal MCP Client
├── streamlit_app.py       # Streamlit UI Client
├── weather_service.py     # Weather API logic
├── requirements.txt       # Project dependencies
└── README.md
```

---

## MCP Tools

### `get_weather`

Returns:

* temperature
* humidity
* wind speed
* weather condition
* 5-day forecast

### `get_temperature`

Returns only the current temperature.

---

## Installation

### Create Virtual Environment

```powershell
uv venv
```

### Activate Virtual Environment

```powershell
.venv\Scripts\activate
```

### Install Dependencies

```powershell
uv pip install -r requirements.txt
```

---

## Run Terminal MCP Client

```powershell
python client.py
```

---

## Run Streamlit UI

```powershell
streamlit run streamlit_app.py
```

Open in browser:

```text
http://localhost:8501
```

---

## API Used

This project uses the Open-Meteo API:

* Free to use
* No API key required
* Provides real-time weather and forecast data

---

## What This Project Demonstrates

This project helps beginners understand:

* MCP (Model Context Protocol)
* MCP Client and MCP Server architecture
* MCP tool discovery
* Tool calling
* AI system communication patterns
* Real-world API integration

---

## Example Workflow

```text
1. User enters city name
2. MCP Client sends tool request
3. MCP Server receives request
4. get_weather tool runs
5. Open-Meteo API returns weather data
6. MCP Server sends response back
7. Client displays weather result
```

---
