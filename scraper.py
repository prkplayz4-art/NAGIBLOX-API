import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# All known Blox Fruits with their prices (Beli & Robux)
FRUIT_DATA = {
    "Bomb":        {"beli": 5000,       "robux": 50,   "rarity": "Common"},
    "Spike":       {"beli": 7500,       "robux": 75,   "rarity": "Common"},
    "Chop":        {"beli": 30000,      "robux": 100,  "rarity": "Common"},
    "Spring":      {"beli": 60000,      "robux": 180,  "rarity": "Common"},
    "Kilo":        {"beli": 5000,       "robux": 50,   "rarity": "Common"},
    "Smoke":       {"beli": 100000,     "robux": 250,  "rarity": "Uncommon"},
    "Spin":        {"beli": 7500,       "robux": 75,   "rarity": "Common"},
    "Flame":       {"beli": 250000,     "robux": 550,  "rarity": "Uncommon"},
    "Ice":         {"beli": 350000,     "robux": 750,  "rarity": "Uncommon"},
    "Sand":        {"beli": 420000,     "robux": 850,  "rarity": "Uncommon"},
    "Dark":        {"beli": 500000,     "robux": 950,  "rarity": "Rare"},
    "Revive":      {"beli": 550000,     "robux": 975,  "rarity": "Rare"},
    "Diamond":     {"beli": 600000,     "robux": 1000, "rarity": "Rare"},
    "Light":       {"beli": 650000,     "robux": 1100, "rarity": "Rare"},
    "Love":        {"beli": 700000,     "robux": 1200, "rarity": "Rare"},
    "Rubber":      {"beli": 750000,     "robux": 1250, "rarity": "Rare"},
    "Barrier":     {"beli": 800000,     "robux": 1350, "rarity": "Rare"},
    "Magma":       {"beli": 850000,     "robux": 1400, "rarity": "Rare"},
    "Quake":       {"beli": 1000000,    "robux": 1500, "rarity": "Rare"},
    "Human":       {"beli": 1000000,    "robux": 1500, "rarity": "Rare"},
    "Buddha":      {"beli": 1250000,    "robux": 1650, "rarity": "Legendary"},
    "String":      {"beli": 1500000,    "robux": 1800, "rarity": "Legendary"},
    "Bird":        {"beli": 1500000,    "robux": 1800, "rarity": "Legendary"},
    "Phoenix":     {"beli": 1800000,    "robux": 2000, "rarity": "Legendary"},
    "Rumble":      {"beli": 2100000,    "robux": 2100, "rarity": "Legendary"},
    "Paw":         {"beli": 2200000,    "robux": 2200, "rarity": "Legendary"},
    "Gravity":     {"beli": 2500000,    "robux": 2300, "rarity": "Legendary"},
    "Dough":       {"beli": 2800000,    "robux": 2400, "rarity": "Legendary"},
    "Shadow":      {"beli": 2900000,    "robux": 2425, "rarity": "Legendary"},
    "Venom":       {"beli": 3000000,    "robux": 2450, "rarity": "Legendary"},
    "Control":     {"beli": 3200000,    "robux": 2475, "rarity": "Legendary"},
    "Soul":        {"beli": 3400000,    "robux": 2550, "rarity": "Legendary"},
    "Dragon":      {"beli": 3500000,    "robux": 2600, "rarity": "Mythical"},
    "Leopard":     {"beli": 5000000,    "robux": 2900, "rarity": "Mythical"},
    "Kitsune":     {"beli": 4000000,    "robux": 2700, "rarity": "Mythical"},
    "T-Rex":       {"beli": 3000000,    "robux": 2500, "rarity": "Mythical"},
    "Spirit":      {"beli": 3800000,    "robux": 2650, "rarity": "Mythical"},
    "Mammoth":     {"beli": 5000000,    "robux": 2900, "rarity": "Mythical"},
    "Blizzard":    {"beli": 2800000,    "robux": 2400, "rarity": "Legendary"},
    "Gas":         {"beli": 3200000,    "robux": 2500, "rarity": "Legendary"},
    "Portal":      {"beli": 1500000,    "robux": 1800, "rarity": "Legendary"},
    "Gravity":     {"beli": 2500000,    "robux": 2300, "rarity": "Legendary"},
}


def enrich_fruit(name: str) -> dict:
    """Add price/rarity info to a fruit name."""
    key = name.strip().title()
    data = FRUIT_DATA.get(key, {})
    return {
        "name": key,
        "beli": data.get("beli", "Unknown"),
        "robux": data.get("robux", "Unknown"),
        "rarity": data.get("rarity", "Unknown"),
    }


def scrape_fandom_wiki() -> dict:
    """Scrape Blox Fruits stock from the Fandom wiki page."""
    url = "https://blox-fruits.fandom.com/wiki/Blox_Fruits_%22Stock%22"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        normal_fruits = []
        mirage_fruits = []

        # Look for table rows with fruit data
        tables = soup.find_all("table", class_=lambda c: c and "wikitable" in c)

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if text and text in FRUIT_DATA:
                        normal_fruits.append(enrich_fruit(text))

        # Also parse infobox or specific divs
        content = soup.find("div", class_="mw-parser-output")
        if content:
            # Find all links that are fruit names
            for link in content.find_all("a"):
                title = link.get("title", "")
                text = link.get_text(strip=True)
                candidate = title or text
                if candidate in FRUIT_DATA:
                    fruit = enrich_fruit(candidate)
                    if fruit not in normal_fruits:
                        normal_fruits.append(fruit)

        return {
            "source": "fandom_wiki",
            "normal": normal_fruits[:4],   # Typically 4 fruits in stock
            "mirage": mirage_fruits[:4],
        }
    except Exception as e:
        return {"source": "fandom_wiki", "error": str(e), "normal": [], "mirage": []}


def scrape_bloxfruitscatalog() -> dict:
    """Scrape from bloxfruitscatalog.com."""
    url = "https://www.bloxfruitscatalog.com/stock"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        normal_fruits = []
        mirage_fruits = []

        # Search for fruit names in the page text
        page_text = soup.get_text()
        lines = [l.strip() for l in page_text.split("\n") if l.strip()]

        in_mirage = False
        for line in lines:
            if "mirage" in line.lower():
                in_mirage = True
            if "normal" in line.lower():
                in_mirage = False

            # Check if line matches a fruit name
            for fruit_name in FRUIT_DATA:
                if fruit_name.lower() == line.lower():
                    enriched = enrich_fruit(fruit_name)
                    if in_mirage:
                        if enriched not in mirage_fruits:
                            mirage_fruits.append(enriched)
                    else:
                        if enriched not in normal_fruits:
                            normal_fruits.append(enriched)

        return {
            "source": "bloxfruitscatalog",
            "normal": normal_fruits,
            "mirage": mirage_fruits,
        }
    except Exception as e:
        return {"source": "bloxfruitscatalog", "error": str(e), "normal": [], "mirage": []}


def scrape_bloxfruitvalues() -> dict:
    """Scrape from bloxfruitvalues.net/stocks."""
    url = "https://www.bloxfruitvalues.net/stocks"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        normal_fruits = []
        mirage_fruits = []

        # Try to find stock sections
        sections = soup.find_all(["section", "div"], class_=re.compile(r"stock|fruit|dealer", re.I))

        for section in sections:
            is_mirage = "mirage" in section.get_text().lower()
            for fruit_name in FRUIT_DATA:
                if re.search(rf"\b{re.escape(fruit_name)}\b", section.get_text(), re.I):
                    enriched = enrich_fruit(fruit_name)
                    if is_mirage:
                        if enriched not in mirage_fruits:
                            mirage_fruits.append(enriched)
                    else:
                        if enriched not in normal_fruits:
                            normal_fruits.append(enriched)

        return {
            "source": "bloxfruitvalues",
            "normal": normal_fruits,
            "mirage": mirage_fruits,
        }
    except Exception as e:
        return {"source": "bloxfruitvalues", "error": str(e), "normal": [], "mirage": []}


def get_stock() -> dict:
    """
    Try multiple sources and return the first one with data.
    Falls back gracefully if a source fails.
    """
    scrapers = [
        scrape_bloxfruitscatalog,
        scrape_bloxfruitvalues,
        scrape_fandom_wiki,
    ]

    results = []
    best = {"normal": [], "mirage": [], "source": "none"}

    for scraper in scrapers:
        result = scraper()
        results.append(result)
        normal_count = len(result.get("normal", []))
        mirage_count = len(result.get("mirage", []))
        total = normal_count + mirage_count

        if total > len(best.get("normal", [])) + len(best.get("mirage", [])):
            best = result

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "normal_stock": best.get("normal", []),
        "mirage_stock": best.get("mirage", []),
        "normal_refresh_hours": 4,
        "mirage_refresh_hours": 2,
        "source_used": best.get("source", "unknown"),
        "all_sources_tried": [r.get("source") for r in results],
        "note": (
            "Normal stock refreshes every 4 hours. "
            "Mirage stock refreshes every 2 hours. "
            "Prices shown in Beli and Robux."
        ),
    }
