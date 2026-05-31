#!/usr/bin/env python3
"""Cliente de ejemplo para la API REST NYC Taxi (Fase 3)."""

from __future__ import annotations

import json
import os
import sys

import requests

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000")


def check_health() -> dict:
    print("=== GET /health ===")
    response = requests.get(f"{BASE_URL}/health", timeout=30)
    data = response.json()
    print(f"Status code: {response.status_code}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()
    return data


def predict_trip(
    vendor_id: int,
    passenger_count: int,
    pickup_lon: float,
    pickup_lat: float,
    dropoff_lon: float,
    dropoff_lat: float,
    pickup_datetime: str,
) -> dict:
    print("=== POST /predict ===")
    payload = {
        "vendor_id": vendor_id,
        "passenger_count": passenger_count,
        "pickup_longitude": pickup_lon,
        "pickup_latitude": pickup_lat,
        "dropoff_longitude": dropoff_lon,
        "dropoff_latitude": dropoff_lat,
        "pickup_datetime": pickup_datetime,
    }
    print(json.dumps(payload, indent=2))
    response = requests.post(f"{BASE_URL}/predict", json=payload, timeout=30)
    data = response.json()
    print(f"\nStatus code: {response.status_code}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()
    return data


def trigger_training() -> dict:
    print("=== POST /train ===")
    response = requests.post(f"{BASE_URL}/train", timeout=30)
    data = response.json()
    print(f"Status code: {response.status_code}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()
    return data


def main() -> int:
    health = check_health()
    if not health.get("model_loaded"):
        print("Advertencia: el modelo no esta cargado. POST /train o copia artefactos a fase-3/model/.")
        return 1

    predict_trip(
        vendor_id=1,
        passenger_count=2,
        pickup_lon=-73.982155,
        pickup_lat=40.767937,
        dropoff_lon=-73.964630,
        dropoff_lat=40.765602,
        pickup_datetime="2016-06-10 09:15:00",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
