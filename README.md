# nyc-taxi-trip-duration

Proyecto de Machine Learning para predecir la duración en segundos de viajes en taxi (NYC Taxi Trip Duration, [Kaggle](https://www.kaggle.com/competitions/nyc-taxi-trip-duration)).

*Proyecto educativo para la asignatura **Modelos de Sistemas I** (entrega por fases: modelo en notebook, contenedor Docker y API REST).*

**Autor:** Jaime Alexis Herrera Ruiz — [jalexis.herrera@udea.edu.co](mailto:jalexis.herrera@udea.edu.co)

## Estructura del repositorio (por ahora)

```text
fase-1/
├── data/              # train.csv de Kaggle (no versionado; ver Fase 1)
├── model/             # artefactos generados por el notebook (no versionados)
├── notebooks/
│   └── modelo_taxi.ipynb
└── requirements.txt
```

## Fase 1 — Modelo predictivo

1. Descarga `train.csv` desde la pestaña **Data** de la competición en Kaggle.
2. Colócalo en `fase-1/data/train.csv`.
3. Crea un entorno virtual e instala dependencias:

   ```bash
   cd fase-1
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Abre y ejecuta el notebook `fase-1/notebooks/modelo_taxi.ipynb` (desde la raíz del repo o desde `fase-1/`; el notebook localiza solo `fase-1/`).

Al final se guardan `fase-1/model/taxi_model.joblib` y `fase-1/model/features.joblib`, listos para la Fase 2.
