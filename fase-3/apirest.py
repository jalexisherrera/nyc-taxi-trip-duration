#!/usr/bin/env python3
"""API REST Flask para prediccion y reentrenamiento del modelo NYC Taxi."""

from __future__ import annotations

import os
import threading
from pathlib import Path

import joblib
from flask import Flask, jsonify, request

from predict import predict_trip_seconds
from train import train_model

app = Flask(__name__)

MODEL_PATH = Path(os.environ.get("MODEL_PATH", "model/taxi_model.joblib"))
FEATURES_PATH = Path(os.environ.get("FEATURES_PATH", "model/features.joblib"))
TRAIN_CSV = Path(os.environ.get("TRAIN_CSV", "data/train.csv"))

REQUIRED_PREDICT_FIELDS = [
    "vendor_id",
    "passenger_count",
    "pickup_longitude",
    "pickup_latitude",
    "dropoff_longitude",
    "dropoff_latitude",
    "pickup_datetime",
]

_model_lock = threading.Lock()
_pipeline = None
_features: list[str] | None = None

_train_lock = threading.Lock()
_train_state = {
    "running": False,
    "error": None,
    "message": None,
}


def _load_model_from_disk() -> tuple[object | None, list[str] | None]:
    """Lee pipeline y lista de features desde disco si existen los archivos."""
    if not MODEL_PATH.is_file() or not FEATURES_PATH.is_file():
        return None, None
    return joblib.load(MODEL_PATH), joblib.load(FEATURES_PATH)


def get_model() -> tuple[object | None, list[str] | None]:
    """Devuelve el modelo en memoria, cargandolo desde disco la primera vez."""
    global _pipeline, _features
    with _model_lock:
        if _pipeline is None:
            _pipeline, _features = _load_model_from_disk()
        return _pipeline, _features


def reload_model() -> tuple[object | None, list[str] | None]:
    """Fuerza recarga del modelo desde disco (tras un reentrenamiento)."""
    global _pipeline, _features
    with _model_lock:
        _pipeline, _features = _load_model_from_disk()
        return _pipeline, _features


def _run_training_job() -> None:
    """Ejecuta entrenamiento en hilo de fondo y actualiza estado compartido."""
    global _train_state
    try:
        train_model(TRAIN_CSV, MODEL_PATH, FEATURES_PATH, test_size=0.2)
        reload_model()
        _train_state["message"] = "Entrenamiento finalizado correctamente."
        _train_state["error"] = None
    except Exception as exc:  # noqa: BLE001 - reportar al cliente HTTP
        _train_state["error"] = str(exc)
        _train_state["message"] = None
    finally:
        _train_state["running"] = False


@app.get("/health")
def health():
    """Indica si la API responde y si hay un modelo cargado en memoria."""
    pipeline, features = get_model()
    return jsonify(
        {
            "status": "ok",
            "model_loaded": pipeline is not None and features is not None,
            "training_running": _train_state["running"],
            "last_training_error": _train_state["error"],
            "last_training_message": _train_state["message"],
        }
    )


@app.post("/predict")
def predict():
    """Predice la duracion de un viaje a partir de un JSON con las features de entrada."""
    pipeline, features = get_model()
    if pipeline is None or features is None:
        return jsonify({"error": "Modelo no encontrado. Entrena primero con POST /train."}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "El cuerpo de la peticion debe ser JSON."}), 400

    missing = [field for field in REQUIRED_PREDICT_FIELDS if field not in data]
    if missing:
        return jsonify({"error": f"Campos faltantes: {missing}"}), 400

    try:
        seconds = predict_trip_seconds(pipeline, features, data)
        return jsonify(
            {
                "predicted_duration_seconds": round(seconds, 2),
                "predicted_duration_minutes": round(seconds / 60.0, 2),
            }
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 400


@app.post("/train")
def train():
    """Inicia reentrenamiento asincrono usando el CSV configurado en TRAIN_CSV."""
    if not TRAIN_CSV.is_file():
        return jsonify({"error": f"No se encontro CSV de entrenamiento: {TRAIN_CSV}"}), 503

    with _train_lock:
        if _train_state["running"]:
            return jsonify({"error": "Ya hay un entrenamiento en curso."}), 409
        _train_state["running"] = True
        _train_state["error"] = None
        _train_state["message"] = None

    thread = threading.Thread(target=_run_training_job, daemon=True)
    thread.start()
    return jsonify({"message": "Entrenamiento iniciado en segundo plano."}), 202


if __name__ == "__main__":
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
