"""
🧪 AgroForgeSIM API tests

Covers core endpoints exposed by the FastAPI service.
Notes:
- Endpoints are prefixed with /api (see backend.app Settings).
- Weather endpoints may return 501 if live weather isn't configured; tests tolerate that.
"""

from typing import Tuple
import pytest


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_crops_schema(client):
    res = client.get("/api/crops")
    assert res.status_code == 200
    data = res.json()
    assert "supported_crop_categories" in data
    assert "total_crops" in data
    assert data["total_crops"] > 0
    assert any("Cereals" == k for k in data["supported_crop_categories"].keys())


def test_surveys_import_echo(client):
    payload = {
        "name": "demo",
        "type": "geojson",
        "features": [{"id": "f1", "name": "Plot A", "geometry": {"type": "Point", "coordinates": [3.13, 6.95]}, "properties": {}}],
    }
    res = client.post("/api/surveys/import", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["name"] == "demo"
    assert data["type"] == "geojson"
    assert isinstance(data["features"], list)


@pytest.mark.parametrize(
    "path,query",
    [
        ("/api/weather/current", {"lat": 6.95, "lon": 3.13}),
        ("/api/weather/forecast", {"lat": 6.95, "lon": 3.13, "hours": 24}),
    ],
)
def test_weather_endpoints_optional(client, path: str, query: dict):
    """
    Weather can be disabled in test builds; accept 200 (active) or 501 (not configured).
    """
    res = client.get(path, params=query)
    assert res.status_code in (200, 501)
