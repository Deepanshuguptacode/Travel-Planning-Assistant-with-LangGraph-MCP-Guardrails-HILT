import os
import shutil
import sys
from pathlib import Path
from typing import Any

import certifi
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient


# =========================================================
# Environment setup
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Support both environment-variable names.
AVIATION_STACK_API_KEY = (
    os.getenv("AVIATION_STACK_API_KEY")
    or os.getenv("AVIATIONSTACK_API_KEY")
)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

WEATHER_SERVER_PATH = BASE_DIR / "custom_weather_mcp_server.py"
HOTEL_SERVER_PATH = BASE_DIR / "custom_hotel_mcp_server.py"
FLIGHT_SERVER_PATH = BASE_DIR / "custom_flight_mcp_server.py"
UVX_COMMAND = shutil.which("uvx") or "uvx"


def _require_env(name: str, value: str | None) -> str:
    """Return an environment value or raise a readable setup error."""

    if not value:
        raise RuntimeError(
            f"{name} is missing. "
            f"Add {name}=your_key to the project .env file."
        )

    return value


def _subprocess_env(**updates: str | None) -> dict[str, str]:
    """
    Preserve the current Windows/Conda environment and add MCP API keys.
    """

    env = os.environ.copy()

    for key, value in updates.items():
        if value:
            env[key] = value

    return env


# =========================================================
# LLM
# =========================================================

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=_require_env("GROQ_API_KEY", GROQ_API_KEY),
    max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "2048")),
)


# =========================================================
# MCP client
# =========================================================

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                str(HOTEL_SERVER_PATH),
            ],
            "env": _subprocess_env(
                GROQ_API_KEY=GROQ_API_KEY,
                GROQ_MODEL=GROQ_MODEL,
                HOTEL_MCP_MODE=os.getenv("HOTEL_MCP_MODE"),
            ),
        },

        "aviationstack": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                str(FLIGHT_SERVER_PATH),
            ],
            "env": _subprocess_env(
                AVIATION_STACK_API_KEY=AVIATION_STACK_API_KEY,
            ),
        },

        "weather": {
            "transport": "stdio",

            # Uses the Python executable from the active Conda environment.
            "command": sys.executable,

            # Uses the weather server inside the current project folder.
            "args": [
                str(WEATHER_SERVER_PATH),
            ],

            "env": _subprocess_env(
                OPENWEATHER_API_KEY=OPENWEATHER_API_KEY,
            ),
        },
    }
)


async def _get_server_tool(
    server_name: str,
    tool_name: str,
):
    """
    Load one tool from one MCP server.

    This prevents a broken weather or AviationStack server from
    crashing an unrelated Tavily request.
    """

    if server_name == "tavily":
        if not HOTEL_SERVER_PATH.is_file():
            raise FileNotFoundError(
                f"Hotel MCP server not found: "
                f"{HOTEL_SERVER_PATH}"
            )

    elif server_name == "aviationstack":
        if not FLIGHT_SERVER_PATH.is_file():
            raise FileNotFoundError(
                f"Flight MCP server not found: "
                f"{FLIGHT_SERVER_PATH}"
            )

    elif server_name == "weather":
        _require_env(
            "OPENWEATHER_API_KEY",
            OPENWEATHER_API_KEY,
        )

        if not WEATHER_SERVER_PATH.is_file():
            raise FileNotFoundError(
                f"Weather MCP server not found: "
                f"{WEATHER_SERVER_PATH}"
            )

    # Important: load only the requested MCP server.
    tools = await client.get_tools(
        server_name=server_name,
    )

    tool = next(
        (
            item
            for item in tools
            if item.name == tool_name
        ),
        None,
    )

    if tool is None:
        available_tools = (
            ", ".join(
                sorted(item.name for item in tools)
            )
            or "none"
        )

        raise RuntimeError(
            f"MCP tool '{tool_name}' was not found "
            f"on server '{server_name}'. "
            f"Available tools: {available_tools}"
        )

    return tool


# =========================================================
# MCP connection test
# =========================================================

async def get_all_tools() -> None:
    """
    Test every MCP server independently.

    One failed server will not stop the remaining tests.
    """

    for server_name in (
        "tavily",
        "aviationstack",
        "weather",
    ):
        try:
            tools = await client.get_tools(
                server_name=server_name,
            )

            tool_names = (
                ", ".join(
                    tool.name
                    for tool in tools
                )
                or "no tools"
            )

            print(
                f"{server_name}: OK -> {tool_names}"
            )

        except Exception as exc:
            print(
                f"{server_name}: FAILED -> "
                f"{type(exc).__name__}: {exc}"
            )


# =========================================================
# Hotel & Search MCP (Replaces external Tavily with local MCP)
# =========================================================

async def tavily_mcp_search(query: str):
    """
    Search for hotel and accommodation options using the local Hotel MCP server.
    Provides automatic fallback to local catalog / generator if MCP subprocess has issues.
    """
    try:
        search_tool = await _get_server_tool(
            "tavily",
            "tavily_search",
        )

        return await search_tool.ainvoke(
            {
                "query": query,
            }
        )
    except Exception as exc:
        print(
            f"[MCP Client] Hotel search via MCP failed ({type(exc).__name__}: {exc}). "
            f"Invoking local fallback generator.",
            flush=True,
        )
        try:
            from custom_hotel_mcp_server import search_hotels_internal
            return search_hotels_internal(query)
        except Exception:
            from custom_hotel_mcp_server import get_dummy_hotel_response
            return get_dummy_hotel_response(query)


# Alias for clearer semantic naming across agents
hotel_mcp_search = tavily_mcp_search


# =========================================================
# AviationStack MCP
# =========================================================

async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict[str, Any] | None = None,
):
    try:
        aviation_tool = await _get_server_tool(
            "aviationstack",
            tool_name,
        )

        return await aviation_tool.ainvoke(
            tool_args or {}
        )
    except Exception as exc:
        print(
            f"[MCP Client] Aviation MCP call '{tool_name}' failed ({type(exc).__name__}: {exc}). "
            f"Using local flight server fallback.",
            flush=True,
        )
        import custom_flight_mcp_server as flight_srv
        if tool_name == "list_airports":
            return flight_srv.list_airports(**(tool_args or {}))
        elif tool_name == "list_airlines":
            return flight_srv.list_airlines(**(tool_args or {}))
        return []


# =========================================================
# Weather MCP
# =========================================================

async def weather_mcp_search(city: str):
    weather_tool = await _get_server_tool(
        "weather",
        "get_current_weather",
    )

    return await weather_tool.ainvoke(
        {
            "city": city,
        }
    )


async def forecast_mcp_search(city: str):
    forecast_tool = await _get_server_tool(
        "weather",
        "get_forecast",
    )

    return await forecast_tool.ainvoke(
        {
            "city": city,
        }
    )


# =========================================================
# Destination extractor
# =========================================================

def extract_destination(query: str) -> str:
    prompt = f"""
Extract only the destination city or country from the travel request.

Travel request:
{query}

Return only the destination name.
Do not add any explanation.
"""

    response = llm.invoke(prompt)

    destination = str(
        response.content
    ).strip()

    if not destination:
        raise ValueError(
            "The destination could not be extracted."
        )

    return destination