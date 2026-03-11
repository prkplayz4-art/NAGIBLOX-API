# 🍎 Blox Fruits Stock API

A Python/FastAPI web scraper that tracks **Normal** and **Mirage** Blox Fruits stock in real-time — with prices in Beli and Robux.

---

## 📦 Features

- ✅ Scrapes Normal stock (refreshes every 4 hours)
- ✅ Scrapes Mirage stock (refreshes every 2 hours)
- ✅ Shows Beli price, Robux price, and Rarity for each fruit
- ✅ Auto-refreshes in the background every 10 minutes
- ✅ Multiple scrape sources with fallback
- ✅ REST API with JSON responses
- ✅ Free to host on Render

---

## 🚀 API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Welcome + list of endpoints |
| `GET /stock` | All stock (Normal + Mirage) |
| `GET /stock/normal` | Normal dealer stock only |
| `GET /stock/mirage` | Mirage dealer stock only |
| `GET /fruits` | All fruits with prices |
| `GET /fruits/{name}` | Single fruit info |
| `GET /refresh` | Force a fresh scrape |
| `GET /health` | Health check |

### Example Response — `/stock`

```json
{
  "timestamp": "2026-03-11T10:00:00+00:00",
  "normal_stock": [
    { "name": "Dough", "beli": 2800000, "robux": 2400, "rarity": "Legendary" },
    { "name": "Shadow", "beli": 2900000, "robux": 2425, "rarity": "Legendary" }
  ],
  "mirage_stock": [
    { "name": "Leopard", "beli": 5000000, "robux": 2900, "rarity": "Mythical" }
  ],
  "normal_refresh_hours": 4,
  "mirage_refresh_hours": 2,
  "source_used": "bloxfruitscatalog"
}
```

---

## 🛠️ Deploy to GitHub + Render

### Step 1 — Push to GitHub

1. Create a new repo on GitHub (e.g. `bloxfruits-stock-api`)
2. Open terminal in this folder and run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bloxfruits-stock-api.git
git push -u origin main
```

### Step 2 — Deploy on Render (Free)

1. Go to [https://render.com](https://render.com) and sign in
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` — click **Deploy**
5. Your API will be live at: `https://bloxfruits-stock-api.onrender.com`

> ⚠️ Free Render plans spin down after 15 min of inactivity.  
> Use [UptimeRobot](https://uptimerobot.com) (free) to ping `/health` every 5 minutes to keep it awake.

---

## 💻 Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit: http://localhost:8000

---

## 🔄 How Auto-Update Works

- On startup, the API scrapes the stock immediately
- A background thread re-scrapes every **10 minutes**
- The `/refresh` endpoint forces an instant re-scrape anytime
- In-game stock rotates every 4h (Normal) and 2h (Mirage), so 10-min polling is more than sufficient

---

## 📂 Project Structure

```
bloxfruits-stock-api/
├── app/
│   ├── __init__.py
│   ├── main.py       ← FastAPI routes
│   └── scraper.py    ← Web scraping logic
├── requirements.txt
├── render.yaml       ← Render deployment config
├── Procfile
└── README.md
```
