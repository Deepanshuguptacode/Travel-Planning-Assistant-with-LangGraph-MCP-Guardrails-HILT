import os
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

mcp = FastMCP("Flight & Aviation MCP Server")

AVIATION_STACK_API_KEY = (
    os.getenv("AVIATION_STACK_API_KEY")
    or os.getenv("AVIATIONSTACK_API_KEY")
)

# Major global airlines dataset
MAJOR_AIRLINES: list[dict[str, str]] = [
    {"name": "Emirates", "iata": "EK", "country": "United Arab Emirates", "hub": "DXB", "alliance": "None"},
    {"name": "Qatar Airways", "iata": "QR", "country": "Qatar", "hub": "DOH", "alliance": "oneworld"},
    {"name": "British Airways", "iata": "BA", "country": "United Kingdom", "hub": "LHR", "alliance": "oneworld"},
    {"name": "Delta Air Lines", "iata": "DL", "country": "United States", "hub": "ATL", "alliance": "SkyTeam"},
    {"name": "United Airlines", "iata": "UA", "country": "United States", "hub": "ORD", "alliance": "Star Alliance"},
    {"name": "American Airlines", "iata": "AA", "country": "United States", "hub": "DFW", "alliance": "oneworld"},
    {"name": "Air France", "iata": "AF", "country": "France", "hub": "CDG", "alliance": "SkyTeam"},
    {"name": "Lufthansa", "iata": "LH", "country": "Germany", "hub": "FRA", "alliance": "Star Alliance"},
    {"name": "Singapore Airlines", "iata": "SQ", "country": "Singapore", "hub": "SIN", "alliance": "Star Alliance"},
    {"name": "Turkish Airlines", "iata": "TK", "country": "Turkey", "hub": "IST", "alliance": "Star Alliance"},
    {"name": "Japan Airlines", "iata": "JL", "country": "Japan", "hub": "HND", "alliance": "oneworld"},
    {"name": "All Nippon Airways", "iata": "NH", "country": "Japan", "hub": "HND", "alliance": "Star Alliance"},
    {"name": "Cathay Pacific", "iata": "CX", "country": "Hong Kong", "hub": "HKG", "alliance": "oneworld"},
    {"name": "KLM Royal Dutch Airlines", "iata": "KL", "country": "Netherlands", "hub": "AMS", "alliance": "SkyTeam"},
    {"name": "Biman Bangladesh Airlines", "iata": "BG", "country": "Bangladesh", "hub": "DAC", "alliance": "None"},
    {"name": "Saudia", "iata": "SV", "country": "Saudi Arabia", "hub": "JED", "alliance": "SkyTeam"},
    {"name": "Etihad Airways", "iata": "EY", "country": "United Arab Emirates", "hub": "AUH", "alliance": "None"},
    {"name": "Swiss International Air Lines", "iata": "LX", "country": "Switzerland", "hub": "ZRH", "alliance": "Star Alliance"},
    {"name": "Qantas", "iata": "QF", "country": "Australia", "hub": "SYD", "alliance": "oneworld"},
    {"name": "Air Canada", "iata": "AC", "country": "Canada", "hub": "YYZ", "alliance": "Star Alliance"},
    {"name": "Air India", "iata": "AI", "country": "India", "hub": "DEL", "alliance": "Star Alliance"},
]

# Major international hub airports
MAJOR_AIRPORTS: list[dict[str, str]] = [
    {"iata": "JFK", "icao": "KJFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "United States"},
    {"iata": "LHR", "icao": "EGLL", "name": "London Heathrow Airport", "city": "London", "country": "United Kingdom"},
    {"iata": "CDG", "icao": "LFPG", "name": "Paris Charles de Gaulle Airport", "city": "Paris", "country": "France"},
    {"iata": "DXB", "icao": "OMDB", "name": "Dubai International Airport", "city": "Dubai", "country": "United Arab Emirates"},
    {"iata": "HND", "icao": "RJTT", "name": "Tokyo Haneda Airport", "city": "Tokyo", "country": "Japan"},
    {"iata": "NRT", "icao": "RJAA", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"},
    {"iata": "SIN", "icao": "WSSS", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
    {"iata": "FRA", "icao": "EDDF", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
    {"iata": "AMS", "icao": "EHAM", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
    {"iata": "IST", "icao": "LTFM", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey"},
    {"iata": "FCO", "icao": "LIRF", "name": "Leonardo da Vinci–Fiumicino Airport", "city": "Rome", "country": "Italy"},
    {"iata": "DAC", "icao": "VGHS", "name": "Hazrat Shahjalal International Airport", "city": "Dhaka", "country": "Bangladesh"},
    {"iata": "LAX", "icao": "KLAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "United States"},
    {"iata": "ORD", "icao": "KORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "United States"},
    {"iata": "DEL", "icao": "VIDP", "name": "Indira Gandhi International Airport", "city": "New Delhi", "country": "India"},
    {"iata": "BKK", "icao": "VTBS", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
    {"iata": "BCN", "icao": "LEBL", "name": "Josep Tarradellas Barcelona-El Prat Airport", "city": "Barcelona", "country": "Spain"},
    {"iata": "SYD", "icao": "YSSY", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia"},
    {"iata": "YYZ", "icao": "CYYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada"},
    {"iata": "MAD", "icao": "LEMD", "name": "Adolfo Suárez Madrid–Barajas Airport", "city": "Madrid", "country": "Spain"},
]


def _try_aviationstack_api(endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]] | None:
    """Attempt live Aviationstack request if API key is present; returns None on failure."""
    if not AVIATION_STACK_API_KEY:
        return None

    try:
        url = f"http://api.aviationstack.com/v1/{endpoint}"
        query_params = {"access_key": AVIATION_STACK_API_KEY, "limit": 25}
        if params:
            query_params.update(params)

        response = requests.get(url, params=query_params, timeout=8)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                return data
        else:
            sys.stderr.write(
                f"[Flight MCP Server] Aviationstack {endpoint} returned status {response.status_code}. Using built-in aviation dataset.\n"
            )
            sys.stderr.flush()
    except Exception as exc:
        sys.stderr.write(
            f"[Flight MCP Server] Aviationstack live call failed ({exc}). Using built-in aviation dataset.\n"
        )
        sys.stderr.flush()

    return None


@mcp.tool()
def list_airports(query: str = "") -> list[dict[str, Any]]:
    """
    List international airports.
    Optional query to filter by city, country, or airport name.
    """
    # 1. Try live API first if available
    live_data = _try_aviationstack_api("airports", {"search": query} if query else None)
    if live_data:
        return [
            {
                "iata": item.get("iata_code") or item.get("iata"),
                "name": item.get("airport_name") or item.get("name"),
                "city": item.get("city_name") or item.get("city"),
                "country": item.get("country_name") or item.get("country"),
            }
            for item in live_data[:20]
        ]

    # 2. Try loading comprehensive airportsdata package if installed
    try:
        import airportsdata
        airports_db = airportsdata.load("IATA")
        if query:
            q_clean = query.strip().lower()
            matched = []
            for code, info in airports_db.items():
                if (
                    q_clean in code.lower()
                    or q_clean in (info.get("city") or "").lower()
                    or q_clean in (info.get("name") or "").lower()
                    or q_clean in (info.get("country") or "").lower()
                ):
                    matched.append(
                        {
                            "iata": code,
                            "name": info.get("name"),
                            "city": info.get("city"),
                            "country": info.get("country"),
                        }
                    )
                if len(matched) >= 25:
                    break
            if matched:
                return matched
    except Exception:
        pass

    # 3. Fallback to curated major hub airports
    if query:
        q_clean = query.strip().lower()
        matched = [
            a for a in MAJOR_AIRPORTS
            if (
                q_clean in a["iata"].lower()
                or q_clean in a["city"].lower()
                or q_clean in a["name"].lower()
                or q_clean in a["country"].lower()
            )
        ]
        if matched:
            return matched

    return MAJOR_AIRPORTS


@mcp.tool()
def list_airlines(query: str = "") -> list[dict[str, Any]]:
    """
    List commercial airlines and route operators.
    Optional query to filter by airline name or country.
    """
    live_data = _try_aviationstack_api("airlines", {"search": query} if query else None)
    if live_data:
        return [
            {
                "name": item.get("airline_name") or item.get("name"),
                "iata": item.get("iata_code") or item.get("iata"),
                "country": item.get("country_name") or item.get("country"),
            }
            for item in live_data[:20]
        ]

    if query:
        q_clean = query.strip().lower()
        matched = [
            a for a in MAJOR_AIRLINES
            if (
                q_clean in a["name"].lower()
                or q_clean in a["iata"].lower()
                or q_clean in a["country"].lower()
            )
        ]
        if matched:
            return matched

    return MAJOR_AIRLINES


if __name__ == "__main__":
    # Launched as a stdio subprocess by MultiServerMCPClient in mcp_client.py
    mcp.run(transport="stdio")
