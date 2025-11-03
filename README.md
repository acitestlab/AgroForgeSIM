# 🌾 AgroForgeSIM

**AgroForgeSIM** is a farm planning and simulation platform inspired by network simulator workflows. Plan fields on a canvas, drag/rotate components (plots, irrigation, weather stations), connect dependencies, and simulate yields against imported land surveys—fusing agronomic parameters with **real-time weather**.

## 🚀 Overview

- Frontend: **React + Vite + TypeScript** with React Flow (drag, rotate, connect)
- Backend: **FastAPI (Python)** with Pydantic models and async engine
- Weather: **Open-Meteo (no key)** with **OpenWeather fallback**
- Import surveys: **GeoJSON/KML/DXF** (via backend converter placeholder)
- **Deployment:** One-command Docker Compose setup for local or production use

---

## ✨ Features

- 🎛️ **Techy-like Canvas** – drag, rotate, and connect farm elements interactively.
- 🌦️ **Weather Integration** – Open-Meteo (no key) or OpenWeather (API key fallback).
- 🧮 **Simulation Engine** – crop growth, water balance, yield projection.
- 🧭 **Survey Import** – load site surveys (GeoJSON/KML/DXF) to create spatial layouts.
- 🌱 **Dynamic Crop Colors** – visualize growth stages and field health.
- 🧑‍🌾 **Harvest Planner** – project readiness, resource demand, and output by acreage.
- 🔒 **Type-Safe API** – Pydantic schemas, async endpoints.
- 🧪 **Test Suite** – pytest for simulation and API coverage.
- 🐳 **Dockerized Deployment** – instant local or production spin-up.

---

## 🧱 Directory Structure (high-level)
AgroForgeSIM/
├── backend/
│   ├── .env
│   ├── app.py
│   ├── cli.py
│   ├── requirements.txt
│   ├── __init__.py
│   │
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── params.py
│   │   ├── sim.py
│   │   ├── harvest.py
│   │   ├── weather.py
│   │   └── utils.py
│   │
│   ├── examples/
│   │   ├── scenario_maize.yaml
│   │   ├── weather_sample.csv
│   │   └── README.md
│   │
│   ├── tests/
│   │   ├── test_simulation.py
│   │   ├── test_api.py
│   │   └── conftest.py
│   │
│   └── logs/
│       └── .gitkeep
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   │
│   ├── public/
│   │   └── styles.css
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api.ts
│       ├── store.ts
│       │
│       ├── canvas/
│       │   ├── FarmCanvas.tsx
│       │   ├── FarmTopology.tsx
│       │   └── sprites.tsx
│       │
│       ├── panels/
│       │   ├── Inspector.tsx
│       │   └── Timeline.tsx
│       │
│       └── components/
│       	 ├── HarvestPlan.tsx
│           ├── Button.tsx
│           ├── Card.tsx
│           └── Loader.tsx
│
├── .gitignore
├── README.md
└── docker-compose.yml

---

## ⚙️ Configuration

### Backend `.env`

```env
# Weather
WEATHER_PROVIDER=open-meteo          # or: openweather
OPENWEATHER_API_KEY=                 # optional

# API
API_PREFIX=/api
API_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

### Frontend .env
VITE_API_BASE_URL=http://localhost:8000/api

# 1️⃣ Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env && vi .env
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# 2️⃣ Frontend
cd ../frontend
npm install
npm run dev -- --host

🐳 Docker Setup
docker compose up --build

Stops containers:
docker compose down
