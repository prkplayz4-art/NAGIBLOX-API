from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
from datetime import datetime, timezone
from app.scraper import get_stock, FRUIT_DATA, enrich_fruit

app = FastAPI(
    title="Blox Fruits Stock API",
    description=(
        "Live Blox Fruits stock tracker — Normal & Mirage dealer. "
        "Auto-refreshes every 2 hours (Mirage) and 4 hours (Normal)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory cache ──────────────────────────────────────────────────────────
_cache: dict = {}
_cache_lock = threading.Lock()
CACHE_TTL_SECONDS = 60 * 10  # re-scrape every 10 minutes


def _refresh_cache():
    global _cache
    data = get_stock()
    with _cache_lock:
        _cache = data
    print(f"[{datetime.now(timezone.utc).isoformat()}] Cache refreshed — "
          f"Normal: {len(data['normal_stock'])} fruits, "
          f"Mirage: {len(data['mirage_stock'])} fruits")


def _background_refresh():
    """Daemon thread: refresh cache every CACHE_TTL_SECONDS."""
    while True:
        time.sleep(CACHE_TTL_SECONDS)
        try:
            _refresh_cache()
        except Exception as e:
            print(f"Background refresh error: {e}")


# Warm up cache on startup
@app.on_event("startup")
def startup_event():
    _refresh_cache()
    t = threading.Thread(target=_background_refresh, daemon=True)
    t.start()


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "message": "🍎 Blox Fruits Stock API",
        "endpoints": {
            "GET /stock":        "All stock (Normal + Mirage)",
            "GET /stock/normal": "Normal dealer stock only",
            "GET /stock/mirage": "Mirage dealer stock only",
            "GET /fruits":       "All fruits with prices",
            "GET /refresh":      "Force a fresh scrape",
            "GET /health":       "Health check",
        },
        "note": "Normal stock refreshes every 4h, Mirage every 2h in-game.",
    }


@app.get("/stock", tags=["Stock"])
def all_stock():
    """Returns both Normal and Mirage stock with prices."""
    with _cache_lock:
        data = dict(_cache)
    if not data:
        raise HTTPException(status_code=503, detail="Cache not ready, try again shortly.")
    return JSONResponse(content=data)


@app.get("/stock/normal", tags=["Stock"])
def normal_stock():
    """Returns only the Normal dealer stock."""
    with _cache_lock:
        data = dict(_cache)
    if not data:
        raise HTTPException(status_code=503, detail="Cache not ready.")
    return JSONResponse(content={
        "timestamp":     data.get("timestamp"),
        "normal_stock":  data.get("normal_stock", []),
        "refresh_every": "4 hours",
        "source":        data.get("source_used"),
    })


@app.get("/stock/mirage", tags=["Stock"])
def mirage_stock():
    """Returns only the Mirage dealer stock."""
    with _cache_lock:
        data = dict(_cache)
    if not data:
        raise HTTPException(status_code=503, detail="Cache not ready.")
    return JSONResponse(content={
        "timestamp":     data.get("timestamp"),
        "mirage_stock":  data.get("mirage_stock", []),
        "refresh_every": "2 hours",
        "source":        data.get("source_used"),
    })


@app.get("/fruits", tags=["Fruits"])
def list_all_fruits():
    """Returns every known Blox Fruit with Beli/Robux prices and rarity."""
    fruits = [enrich_fruit(name) for name in FRUIT_DATA]
    return JSONResponse(content={
        "count":  len(fruits),
        "fruits": fruits,
    })


@app.get("/fruits/{name}", tags=["Fruits"])
def get_fruit(name: str):
    """Get info for a specific fruit by name."""
    key = name.strip().title()
    if key not in FRUIT_DATA:
        raise HTTPException(status_code=404, detail=f"Fruit '{key}' not found.")
    return JSONResponse(content=enrich_fruit(key))


@app.get("/refresh", tags=["Admin"])
def force_refresh():
    """Force a fresh scrape immediately (bypasses cache TTL)."""
    _refresh_cache()
    with _cache_lock:
        data = dict(_cache)
    return JSONResponse(content={
        "message": "Cache refreshed successfully.",
        "timestamp": data.get("timestamp"),
        "normal_count": len(data.get("normal_stock", [])),
        "mirage_count": len(data.get("mirage_stock", [])),
    })


@app.get("/health", tags=["Admin"])
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
