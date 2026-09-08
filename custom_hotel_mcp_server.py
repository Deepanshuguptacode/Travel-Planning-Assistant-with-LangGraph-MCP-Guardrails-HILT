import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

mcp = FastMCP("Hotel & Search MCP Server")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
HOTEL_MCP_MODE = os.getenv("HOTEL_MCP_MODE", "auto").strip().lower()

# =========================================================
# Curated dummy hotel catalog for common travel destinations
# =========================================================

CURATED_HOTELS: dict[str, list[dict[str, str]]] = {
    "paris": [
        {
            "name": "CitizenM Paris Gare de Lyon",
            "category": "Budget / Trendy",
            "neighborhood": "12th Arrondissement (Bercy / Gare de Lyon)",
            "price_per_night": "EUR 130 - 180 (~$140 - $195)",
            "amenities": "Free Wi-Fi, Rooftop Bar, 24/7 Canteen, XL King Beds, MoodPad controls",
            "summary": "Modern, design-forward rooms with great transport links across Paris.",
        },
        {
            "name": "Hotel Monge",
            "category": "Boutique / Mid-Range",
            "neighborhood": "5th Arrondissement (Latin Quarter)",
            "price_per_night": "EUR 220 - 320 (~$240 - $350)",
            "amenities": "Hammam Spa, Honesty Bar, Tea Salon, Breakfast Buffet, Designer Toiletries",
            "summary": "Charming Parisian town-house feel near Jardin des Plantes and the Pantheon.",
        },
        {
            "name": "Le Pavillon de la Reine",
            "category": "Luxury & Spa",
            "neighborhood": "3rd Arrondissement (Place des Vosges / Le Marais)",
            "price_per_night": "EUR 480 - 750 (~$520 - $815)",
            "amenities": "Michelin-starred dining, Codage Spa, Courtyard Garden, Valet Parking",
            "summary": "Romantic historic 5-star haven tucked away on historic Place des Vosges.",
        },
    ],
    "tokyo": [
        {
            "name": "Hotel Gracery Shinjuku",
            "category": "Mid-Range / Iconic",
            "neighborhood": "Shinjuku (Kabukicho)",
            "price_per_night": "JPY 18,000 - 28,000 (~$120 - $190)",
            "amenities": "Godzilla Head Terrace, Concierge, High-speed Wi-Fi, Multiple Onsite Restaurants",
            "summary": "Famous landmark hotel steps from Shinjuku Station, ideal for nightlife and transit.",
        },
        {
            "name": "The Gate Hotel Asakusa Kaminarimon",
            "category": "Boutique / Scenic",
            "neighborhood": "Asakusa (Taito)",
            "price_per_night": "JPY 22,000 - 34,000 (~$150 - $230)",
            "amenities": "13th-floor Panorama Terrace with Skytree views, French-inspired Bistro, Rain Showers",
            "summary": "Stylish boutique hotel opposite historic Senso-ji temple and Kaminarimon gate.",
        },
        {
            "name": "Park Hyatt Tokyo",
            "category": "Ultra Luxury",
            "neighborhood": "Nishi-Shinjuku",
            "price_per_night": "JPY 90,000 - 160,000 (~$600 - $1,100)",
            "amenities": "Peak Bar with panoramic city skyline, Club on the Park Spa & Pool, Gourmet Dining",
            "summary": "World-renowned luxury high above Tokyo, famed for legendary service and sweeping views.",
        },
    ],
    "london": [
        {
            "name": "The Hoxton, Holborn",
            "category": "Boutique / Lifestyle",
            "neighborhood": "Holborn / Covent Garden",
            "price_per_night": "GBP 180 - 260 (~$230 - $335)",
            "amenities": "Vibrant Lobby Lounge, Rondo Restaurant, Pet-friendly, Workspaces, Rain Showers",
            "summary": "Buzzing neighborhood hub close to British Museum and West End theatres.",
        },
        {
            "name": "Treehouse Hotel London",
            "category": "Unique / Mid-Range",
            "neighborhood": "Marylebone / Regent Street",
            "price_per_night": "GBP 240 - 350 (~$310 - $450)",
            "amenities": "Madera Rooftop Restaurant, Plant-filled decor, Views of The Shard & London Eye",
            "summary": "Playful, nature-themed design with spectacular 360-degree skyline views.",
        },
        {
            "name": "The Savoy",
            "category": "Iconic Luxury",
            "neighborhood": "Strand / Westminster",
            "price_per_night": "GBP 650 - 1,100 (~$840 - $1,420)",
            "amenities": "Butler Service, American Bar, River Thames views, Indoor Pool, Spa",
            "summary": "Quintessential British glamour on the banks of the Thames with historic heritage.",
        },
    ],
    "new york": [
        {
            "name": "Arlo SoHo",
            "category": "Micro-Boutique / Trendy",
            "neighborhood": "SoHo / Hudson Square",
            "price_per_night": "$210 - $320",
            "amenities": "Rooftop Bar (A.R.T.), Courtyard, Bodega Cafe, Free Bicycles",
            "summary": "Smart micro-hotel in trendy downtown Manhattan near art galleries and boutiques.",
        },
        {
            "name": "The Beekman, A Thompson Hotel",
            "category": "Historic Luxury / Mid-High",
            "neighborhood": "Financial District / City Hall",
            "price_per_night": "$360 - $550",
            "amenities": "Nine-story Victorian Atrium, Temple Court by Tom Colicchio, Fitness Center",
            "summary": "Architectural masterpiece with vintage charm and renowned culinary offerings.",
        },
        {
            "name": "The Plaza Hotel",
            "category": "Grand Luxury",
            "neighborhood": "Midtown East (Fifth Ave & Central Park South)",
            "price_per_night": "$750 - $1,400",
            "amenities": "Guerlain Spa, Palm Court Afternoon Tea, 24-hr Butler Service, Central Park views",
            "summary": "Legendary New York icon offering timeless Fifth Avenue luxury.",
        },
    ],
    "rome": [
        {
            "name": "Hotel Artemide",
            "category": "Mid-Range / Highly Rated",
            "neighborhood": "Via Nazionale / Repubblica",
            "price_per_night": "EUR 160 - 260 (~$175 - $285)",
            "amenities": "Ambrosia Rooftop Restaurant, Artemis Spa, Free Minibar, Full Breakfast",
            "summary": "Exceptional hospitality within walking distance of the Colosseum and Trevi Fountain.",
        },
        {
            "name": "The Hoxton, Rome",
            "category": "Boutique / Contemporary",
            "neighborhood": "Parioli / Villa Borghese",
            "price_per_night": "EUR 180 - 290 (~$195 - $315)",
            "amenities": "Beverly Restaurant, Outdoor Terrace, Mid-century Italian design, Coffee Bar",
            "summary": "Chic, leafy retreat near Villa Borghese gardens and museums.",
        },
        {
            "name": "Hotel de Russie, a Rocco Forte Hotel",
            "category": "Classic Luxury",
            "neighborhood": "Piazza del Popolo / Spanish Steps",
            "price_per_night": "EUR 600 - 1,200 (~$650 - $1,300)",
            "amenities": "Secret Tiered Garden, Le Jardin de Russie, Wellness Zone & Saltwater Pool",
            "summary": "Celebrity-favorite sanctuary featuring one of the most enchanted gardens in Rome.",
        },
    ],
    "dubai": [
        {
            "name": "Rove Downtown",
            "category": "Budget / Lifestyle",
            "neighborhood": "Downtown Dubai",
            "price_per_night": "AED 350 - AED 600 (~$95 - $160)",
            "amenities": "Outdoor Pool facing Burj Khalifa, 24/7 Gym, Laundromat, The Daily Cafe",
            "summary": "Clean, contemporary, and value-packed hotel directly opposite Dubai Mall.",
        },
        {
            "name": "25hours Hotel Dubai One Central",
            "category": "Boutique / Creative",
            "neighborhood": "Trade Centre / Museum of the Future",
            "price_per_night": "AED 650 - AED 1,100 (~$175 - $300)",
            "amenities": "Rooftop Pool with Museum views, Monkey Bar, Pottery Studio, Sauna & Spa",
            "summary": "Eclectic, vibrant urban escape rich in art, books, and quirky design.",
        },
        {
            "name": "Address Downtown",
            "category": "Luxury",
            "neighborhood": "Downtown Dubai",
            "price_per_night": "AED 1,400 - AED 2,800 (~$380 - $760)",
            "amenities": "Direct Dubai Mall link, Infinity Pool facing Burj Khalifa, Luxury Spa",
            "summary": "Premier 5-star destination with front-row views of the Dubai Fountains.",
        },
    ],
    "dhaka": [
        {
            "name": "Hotel 71",
            "category": "Budget / Central",
            "neighborhood": "Bijoynagar / Motijheel",
            "price_per_night": "BDT 3,500 - BDT 6,000 (~$30 - $55)",
            "amenities": "Free Breakfast, High-Speed Wi-Fi, Rooftop Restaurant, Airport Pickup",
            "summary": "Popular budget hotel with friendly service close to Old Dhaka and commercial hub.",
        },
        {
            "name": "Pan Pacific Sonargaon Dhaka",
            "category": "Classic Luxury / Business",
            "neighborhood": "Kawran Bazar / Central Dhaka",
            "price_per_night": "BDT 12,000 - BDT 20,000 (~$100 - $170)",
            "amenities": "Outdoor Swimming Pool, Health Club & Spa, Multi-Cuisine Restaurants, Oasis Lounge",
            "summary": "Well-established 5-star haven with landscaped gardens in the heart of Dhaka.",
        },
        {
            "name": "The Westin Dhaka",
            "category": "Modern Luxury",
            "neighborhood": "Gulshan-2 (Diplomatic Zone)",
            "price_per_night": "BDT 18,000 - BDT 28,000 (~$150 - $240)",
            "amenities": "Heavenly Bed & Spa, Heated Outdoor Pool, Prego Italian Restaurant, High Security",
            "summary": "Sophisticated hotel in Dhaka's premier diplomatic and dining district.",
        },
    ],
}


def _extract_destination_candidate(query: str) -> str:
    """Extract the main destination candidate from a search query."""
    cleaned = re.sub(
        r"(?i)\b(best|top|budget|luxury|cheap|recommended|hotels?|for|in|near|around|stay|accommodations?|resorts?|lodging|to|visiting|trip)\b",
        " ",
        query,
    )
    words = [w for w in cleaned.strip().split() if len(w) > 2]
    return " ".join(words[:3]) if words else query.strip()


def _format_dummy_hotels(destination_name: str, hotels: list[dict[str, str]]) -> str:
    """Format structured hotel records into a readable markdown response."""
    output = [
        f"### Hotel & Accommodation Recommendations for {destination_name.title()}",
        "_Source: Local Hotel MCP Server (Curated Accommodations Catalog)_",
        "",
    ]

    for idx, hotel in enumerate(hotels, start=1):
        output.extend(
            [
                f"**{idx}. {hotel['name']}** ({hotel['category']})",
                f"- **Neighborhood / Area**: {hotel['neighborhood']}",
                f"- **Estimated Price**: {hotel['price_per_night']}",
                f"- **Amenities**: {hotel['amenities']}",
                f"- **Overview**: {hotel['summary']}",
                "",
            ]
        )

    output.append(
        "> [!NOTE]\n"
        "> Prices are approximate estimates and may vary by season, booking date, and availability."
    )
    return "\n".join(output)


def _generate_procedural_dummy(destination: str) -> str:
    """Generate realistic dummy hotel options for any destination."""
    dest_clean = destination.strip().title() or "Your Destination"
    procedural_hotels = [
        {
            "name": f"{dest_clean} City Central Inn",
            "category": "Budget / Convenient",
            "neighborhood": f"Downtown / Central {dest_clean}",
            "price_per_night": "$55 - $90 / night",
            "amenities": "Free Wi-Fi, Express Breakfast, 24/7 Front Desk, Air Conditioning",
            "summary": f"Great value accommodation within easy walking distance of {dest_clean} transport hubs and local eateries.",
        },
        {
            "name": f"The Grand {dest_clean} Boutique Hotel",
            "category": "Boutique / Mid-Range",
            "neighborhood": f"Historic Arts & Cultural Quarter, {dest_clean}",
            "price_per_night": "$130 - $210 / night",
            "amenities": "Rooftop Terrace, Artisan Breakfast, Fitness Room, Concierge Desk",
            "summary": f"Warmly rated boutique stay offering stylish decor and authentic local hospitality in {dest_clean}.",
        },
        {
            "name": f"Royal {dest_clean} Palace Resort & Spa",
            "category": "Luxury / 5-Star",
            "neighborhood": f"Prime Waterfront / Landmark District, {dest_clean}",
            "price_per_night": "$320 - $550 / night",
            "amenities": "Full-Service Spa & Wellness Pool, Fine Dining Restaurants, Valet, Executive Lounge",
            "summary": f"Premier luxury experience with top-tier amenities and panoramic views of {dest_clean}.",
        },
    ]
    return _format_dummy_hotels(dest_clean, procedural_hotels)


def get_dummy_hotel_response(query: str) -> str:
    """Match query against curated catalog or generate procedural dummy response."""
    query_lower = query.lower()

    for key, hotels in CURATED_HOTELS.items():
        if key in query_lower:
            return _format_dummy_hotels(key.title(), hotels)

    candidate = _extract_destination_candidate(query)
    for key, hotels in CURATED_HOTELS.items():
        if key in candidate.lower():
            return _format_dummy_hotels(key.title(), hotels)

    return _generate_procedural_dummy(candidate)


def _generate_llm_hotel_response(query: str) -> str:
    """Invoke Groq LLM to synthesize realistic hotel recommendations for the query."""
    if not GROQ_API_KEY or "your_groq_api_key_here" in GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured or is a placeholder.")

    from langchain_groq import ChatGroq

    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    llm = ChatGroq(
        model=model_name,
        api_key=GROQ_API_KEY,
        temperature=0.3,
        max_tokens=1024,
    )

    prompt = f"""You are an expert travel accommodation advisor. Provide 3 to 4 recommended hotels based on the user's travel query:
"{query}"

Cover a sensible range of choices (e.g. Budget/Value, Mid-range/Boutique, and Luxury/Premium).

Format your response cleanly with:
### Hotel & Accommodation Recommendations
For each hotel:
- **[Hotel Name]** ([Category, e.g. Budget / Boutique / Luxury])
- **Neighborhood / Area**: [Specific neighborhood or landmark proximity]
- **Estimated Price**: [Approximate price per night in local currency & USD equivalent]
- **Amenities**: [Key amenities e.g. Wi-Fi, breakfast, pool, transport links]
- **Overview**: [1-2 sentences on why it is recommended for this trip]

Conclude with a brief practical booking tip. Keep it factual, realistic, and concise."""

    response = llm.invoke(prompt)
    content = str(response.content).strip()
    if not content:
        raise ValueError("LLM returned an empty response.")
    return content


def search_hotels_internal(query: str) -> str:
    """
    Search hotels using LLM or Dummy response based on HOTEL_MCP_MODE and key availability.
    - 'dummy': Always return curated dummy response.
    - 'llm': Always use LLM (raises if unavailable).
    - 'auto': Try LLM; if fails or unconfigured, seamlessly return dummy response.
    """
    mode = HOTEL_MCP_MODE

    if mode == "dummy":
        return get_dummy_hotel_response(query)

    if mode == "llm":
        return _generate_llm_hotel_response(query)

    # Default 'auto' mode: attempt LLM first, gracefully fallback to dummy
    try:
        if GROQ_API_KEY and "your_groq_api_key_here" not in GROQ_API_KEY:
            return _generate_llm_hotel_response(query)
    except Exception as exc:
        import sys
        sys.stderr.write(
            f"[Hotel MCP Server] LLM generation skipped ({exc}), falling back to curated dummy catalog.\n"
        )
        sys.stderr.flush()

    return get_dummy_hotel_response(query)


# =========================================================
# MCP Tools
# =========================================================

@mcp.tool()
def tavily_search(query: str) -> str:
    """
    Search for hotel and accommodation recommendations for travel planning.
    Replaces external Tavily API with local LLM or curated dummy data.
    """
    query = (query or "").strip()
    if not query:
        return "Please provide a destination or hotel query."
    return search_hotels_internal(query)


@mcp.tool()
def hotel_search(query: str) -> str:
    """
    Search for hotels, resorts, and accommodation options for a given destination.
    """
    return tavily_search(query)


if __name__ == "__main__":
    # Launched as a stdio subprocess by MultiServerMCPClient in mcp_client.py
    mcp.run(transport="stdio")
