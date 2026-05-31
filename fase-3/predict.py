#!/usr/bin/env python3
"""Genera predicciones desde un CSV usando un modelo entrenado."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

PREDICTION_COLUMN = "predicted_trip_duration"


def haversine_distance(lat1: pd.Series, lon1: pd.Series, lat2: pd.Series, lon2: pd.Series) -> np.ndarray:
    """Calcula distancia en km entre coordenadas usando Haversine."""
    radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return radius_km * c


def build_prediction_frame(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Valida columnas de entrada y construye features para inferencia."""
    required_cols = [
        "vendor_id",
        "passenger_count",
        "pickup_datetime",
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
    ]
    missing = [c for c in required_cols if c not in raw_df.columns]
    if missing:
        raise ValueError(f"Faltan columnas obligatorias en predict CSV: {missing}")

    df = raw_df.copy()
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df["vendor_id"] = pd.to_numeric(df["vendor_id"], errors="coerce")
    df["passenger_count"] = pd.to_numeric(df["passenger_count"], errors="coerce")

    for col in ["pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["distance_km"] = haversine_distance(
        df["pickup_latitude"],
        df["pickup_longitude"],
        df["dropoff_latitude"],
        df["dropoff_longitude"],
    )
    df["hour"] = df["pickup_datetime"].dt.hour
    df["day_of_week"] = df["pickup_datetime"].dt.dayofweek
    df["month"] = df["pickup_datetime"].dt.month

    return df


def predict_trip_seconds(model, feature_names: list[str], trip: dict) -> float:
    """Predice la duracion en segundos para un viaje recibido como diccionario."""
    prepared = build_prediction_frame(pd.DataFrame([trip]))
    x = prepared[feature_names].fillna(0.0)
    pred_log = model.predict(x)
    return float(np.maximum(np.expm1(pred_log[0]), 0.0))


def run_prediction(input_csv: Path, output_csv: Path, model_path: Path, features_path: Path) -> None:
    """Genera predicciones por fila y escribe CSV con predicted_trip_duration."""
    model = joblib.load(model_path)
    features = joblib.load(features_path)

    raw_df = pd.read_csv(input_csv)
    prepared_df = build_prediction_frame(raw_df)
    x = prepared_df[features]

    # Valores faltantes tras parseo se completan para evitar fallos en inferencia por filas invalidas.
    x = x.fillna(0.0)

    pred_log = model.predict(x)
    pred_seconds = np.maximum(np.expm1(pred_log), 0.0)

    result_df = raw_df.copy()
    result_df[PREDICTION_COLUMN] = pred_seconds

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_csv, index=False)

    print(f"Predicciones generadas: {len(result_df)}")
    print(f"Archivo de salida: {output_csv}")


def parse_args() -> argparse.Namespace:
    """Define y parsea los argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(description="Realiza predicciones de trip_duration desde un CSV de entrada.")
    parser.add_argument("--input-csv", required=True, type=Path, help="Ruta al CSV con datos de entrada.")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("predictions.csv"),
        help="Ruta del CSV de salida con las predicciones.",
    )
    parser.add_argument("--model-path", type=Path, default=Path("model/taxi_model.joblib"), help="Ruta del modelo.")
    parser.add_argument(
        "--features-path",
        type=Path,
        default=Path("model/features.joblib"),
        help="Ruta de lista de features.",
    )
    return parser.parse_args()


def main() -> None:
    """Punto de entrada CLI: carga modelo y escribe archivo de predicciones."""
    args = parse_args()
    run_prediction(args.input_csv, args.output_csv, args.model_path, args.features_path)


if __name__ == "__main__":
    main()
