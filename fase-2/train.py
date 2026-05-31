#!/usr/bin/env python3
"""Entrena y guarda el modelo de duracion de viajes NYC Taxi."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
FEATURES = [
    "vendor_id",
    "passenger_count",
    "pickup_longitude",
    "pickup_latitude",
    "dropoff_longitude",
    "dropoff_latitude",
    "distance_km",
    "hour",
    "day_of_week",
    "month",
]


def haversine_distance(lat1: pd.Series, lon1: pd.Series, lat2: pd.Series, lon2: pd.Series) -> np.ndarray:
    """Calcula distancia en km entre coordenadas usando Haversine."""
    radius_km = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return radius_km * c


def build_training_frame(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Genera dataframe de entrenamiento con las features requeridas."""
    required_cols = [
        "vendor_id",
        "passenger_count",
        "pickup_datetime",
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
        "trip_duration",
    ]
    missing = [c for c in required_cols if c not in raw_df.columns]
    if missing:
        raise ValueError(f"Faltan columnas obligatorias en train CSV: {missing}")

    df = raw_df.copy()
    df = df.dropna(subset=required_cols)
    df = df[(df["trip_duration"] >= 10) & (df["trip_duration"] <= 7200)]

    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df = df.dropna(subset=["pickup_datetime"])

    df["vendor_id"] = pd.to_numeric(df["vendor_id"], errors="coerce")
    df["passenger_count"] = pd.to_numeric(df["passenger_count"], errors="coerce")
    for col in ["pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=[
            "vendor_id",
            "passenger_count",
            "pickup_longitude",
            "pickup_latitude",
            "dropoff_longitude",
            "dropoff_latitude",
        ]
    )

    df["distance_km"] = haversine_distance(
        df["pickup_latitude"],
        df["pickup_longitude"],
        df["dropoff_latitude"],
        df["dropoff_longitude"],
    )
    df["hour"] = df["pickup_datetime"].dt.hour
    df["day_of_week"] = df["pickup_datetime"].dt.dayofweek
    df["month"] = df["pickup_datetime"].dt.month
    df["log_duration"] = np.log1p(df["trip_duration"])

    return df


def train_model(train_csv: Path, model_path: Path, features_path: Path, test_size: float) -> None:
    """Entrena el pipeline, evalua metricas en hold-out y guarda modelo y features."""
    raw_df = pd.read_csv(train_csv)
    df = build_training_frame(raw_df)
    if df.empty:
        raise ValueError("No hay filas validas despues de limpieza/preprocesamiento.")

    x = df[FEATURES]
    y = df["log_duration"]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
    )

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    n_jobs=-1,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    pipeline.fit(x_train, y_train)

    y_pred_log = pipeline.predict(x_test)
    rmse_log = root_mean_squared_error(y_test, y_pred_log)
    y_test_seconds = np.expm1(y_test)
    y_pred_seconds = np.expm1(y_pred_log)
    mae_seconds = mean_absolute_error(y_test_seconds, y_pred_seconds)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    features_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    joblib.dump(FEATURES, features_path)

    print(f"Filas usadas para entrenamiento: {len(df)}")
    print(f"Train/Test: {len(x_train)} / {len(x_test)}")
    print(f"RMSE (log): {rmse_log:.4f}")
    print(f"MAE (segundos): {mae_seconds:.2f}")
    print(f"Modelo guardado en: {model_path}")
    print(f"Features guardadas en: {features_path}")


def parse_args() -> argparse.Namespace:
    """Define y parsea los argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(description="Reentrena modelo NYC Taxi y guarda artefactos en disco.")
    parser.add_argument("--train-csv", required=True, type=Path, help="Ruta al CSV con datos de entrenamiento.")
    parser.add_argument("--model-out", type=Path, default=Path("model/taxi_model.joblib"), help="Ruta salida modelo.")
    parser.add_argument(
        "--features-out",
        type=Path,
        default=Path("model/features.joblib"),
        help="Ruta salida lista de features.",
    )
    parser.add_argument("--test-size", type=float, default=0.2, help="Proporcion de test para evaluacion.")
    return parser.parse_args()


def main() -> None:
    """Punto de entrada CLI: entrena y persiste artefactos segun argumentos."""
    args = parse_args()
    train_model(args.train_csv, args.model_out, args.features_out, args.test_size)


if __name__ == "__main__":
    main()
