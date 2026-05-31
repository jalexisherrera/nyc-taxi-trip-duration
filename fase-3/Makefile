IMAGE_NAME=nyc-taxi-fase3
TRAIN_CSV=data/train.csv
MODEL_PATH=model/taxi_model.joblib
FEATURES_PATH=model/features.joblib

.PHONY: help build up down logs health predict-cli train-api client shell

help:
	@echo "Comandos Fase 3 (API REST):"
	@echo "  make build        -> construye imagen"
	@echo "  make up           -> levanta API en http://localhost:5000"
	@echo "  make down         -> detiene contenedor"
	@echo "  make logs         -> logs del servicio"
	@echo "  make health       -> GET /health"
	@echo "  make predict-cli  -> POST /predict de ejemplo (curl)"
	@echo "  make train-api    -> POST /train (requiere $(TRAIN_CSV))"
	@echo "  make client       -> ejecuta client.py contra localhost:5000"
	@echo "  make shell        -> bash en el contenedor"

build:
	podman compose build

up:
	podman compose up -d

down:
	podman compose down

logs:
	podman compose logs -f taxi-api

health:
	curl -s http://localhost:5000/health | python3 -m json.tool

predict-cli:
	curl -s -X POST http://localhost:5000/predict \
		-H "Content-Type: application/json" \
		-d '{"vendor_id":1,"passenger_count":2,"pickup_longitude":-73.982155,"pickup_latitude":40.767937,"dropoff_longitude":-73.964630,"dropoff_latitude":40.765602,"pickup_datetime":"2016-06-10 09:15:00"}' \
		| python3 -m json.tool

train-api:
	curl -s -X POST http://localhost:5000/train | python3 -m json.tool

client:
	python3 client.py

shell:
	podman compose run --rm --entrypoint /bin/bash taxi-api
