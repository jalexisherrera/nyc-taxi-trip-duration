# nyc-taxi-trip-duration

Proyecto de Machine Learning para predecir la duración en segundos de viajes en taxi (NYC Taxi Trip Duration, [Kaggle](https://www.kaggle.com/competitions/nyc-taxi-trip-duration)).

*Proyecto educativo para la asignatura **Modelos de Sistemas I** (entrega por fases: modelo en notebook, contenedor Docker y API REST).*

**Autor:** Jaime Alexis Herrera Ruiz — [jalexis.herrera@udea.edu.co](mailto:jalexis.herrera@udea.edu.co)

## Estructura del repositorio

```text
fase-1/
├── data/              # train.csv de Kaggle (no versionado; ver Fase 1)
├── model/             # artefactos generados por el notebook (no versionados)
├── notebooks/
│   └── modelo_taxi.ipynb
└── requirements.txt
fase-2/
├── Dockerfile
├── compose.yaml
├── Makefile
├── train.py
├── predict.py
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

## Fase 2 - Despliegue en contenedor Docker

La Fase 2 incluye:
- `train.py`: reentrena el modelo desde un CSV con etiquetas (`trip_duration`) y guarda una nueva version del modelo.
- `predict.py`: carga un modelo almacenado y genera una prediccion por cada fila de un CSV de entrada.
- `Dockerfile`: imagen con todo lo necesario para ejecutar ambos scripts.
- `compose.yaml`: configuracion compatible con `docker compose` y `podman compose`.
- `Makefile`: comandos cortos para construir, entrenar y predecir.

### Antes de comenzar (obligatorio)

Para ejecutar la Fase 2 necesitas tener instalado al menos uno de estos motores de contenedores:
- Docker
- Podman

Verifica con:

```bash
docker --version || true
podman --version || true
```

Si ambos comandos fallan, primero instala Docker o Podman y luego continua con los pasos de esta fase.

### Requisitos previos

```bash
docker --version
docker compose version
podman --version
podman compose version
make --version
```

### Fedora: instalacion recomendada con Podman Compose

Si estas en Fedora y usas Podman:

```bash
sudo dnf install -y podman podman-compose make
```

Luego verifica:

```bash
podman --version
podman compose version
```

### 1) Construir la imagen (opcion recomendada)

```bash
cd fase-2
make build
```

Comando equivalente sin `make`:

```bash
docker build -t nyc-taxi-fase2 .
```

### 2) Entrenar dentro del contenedor

Coloca `train.csv` en `fase-2/data/train.csv` y ejecuta:

```bash
make train
```

Comando equivalente sin `make`:

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/model:/app/model" \
  nyc-taxi-fase2 \
  train.py \
  --train-csv /app/data/train.csv \
  --model-out /app/model/taxi_model.joblib \
  --features-out /app/model/features.joblib
```

### 3) Predecir dentro del contenedor

Coloca tu archivo de entrada en `fase-2/data/input.csv` y ejecuta:

```bash
make predict
```

Comando equivalente sin `make`:

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/model:/app/model" \
  -v "$(pwd)/output:/app/output" \
  nyc-taxi-fase2 \
  predict.py \
  --input-csv /app/data/input.csv \
  --output-csv /app/output/predictions.csv \
  --model-path /app/model/taxi_model.joblib \
  --features-path /app/model/features.joblib
```

El resultado queda en `fase-2/output/predictions.csv` con la columna `predicted_trip_duration`.

### Flujo con Podman Compose (Fedora)

Desde `fase-2/`:

```bash
make compose-build
make compose-train
make compose-predict
```

Comandos equivalentes sin `make`:

```bash
podman compose build
podman compose run --rm taxi train.py --train-csv /app/data/train.csv --model-out /app/model/taxi_model.joblib --features-out /app/model/features.joblib
podman compose run --rm taxi predict.py --input-csv /app/data/input.csv --output-csv /app/output/predictions.csv --model-path /app/model/taxi_model.joblib --features-path /app/model/features.joblib
```

Nota: en Fedora con SELinux, `compose.yaml` ya incluye `:Z` en los volumenes para evitar errores de permisos (`Permission denied`) al leer/escribir archivos montados.

### Notas para principiantes

- El contenedor ya crea `/app/data`, `/app/model` y `/app/output` automaticamente.
- Tus archivos reales viven en tu maquina local (`fase-2/data`, `fase-2/model`, `fase-2/output`) y se conectan al contenedor con `-v`.
- El `ENTRYPOINT ["python"]` permite ejecutar scripts mas corto (`train.py` y `predict.py`) sin escribir `python` cada vez.
- Puedes ver todos los comandos disponibles con:

  ```bash
  make help
  ```
