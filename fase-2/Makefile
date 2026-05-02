IMAGE_NAME=nyc-taxi-fase2
TRAIN_CSV=data/train.csv
INPUT_CSV=data/input.csv
MODEL_PATH=model/taxi_model.joblib
FEATURES_PATH=model/features.joblib
PREDICTIONS_CSV=output/predictions.csv

.PHONY: help build train predict shell compose-build compose-train compose-predict

help:
	@echo "Comandos disponibles:"
	@echo "  make build   -> construye imagen Docker"
	@echo "  make train   -> entrena modelo (requiere $(TRAIN_CSV))"
	@echo "  make predict -> genera predicciones (requiere $(INPUT_CSV) y modelo)"
	@echo "  make shell   -> abre shell interactiva dentro del contenedor"
	@echo "  make compose-build   -> construye con podman compose"
	@echo "  make compose-train   -> entrena con podman compose"
	@echo "  make compose-predict -> predice con podman compose"

build:
	docker build -t $(IMAGE_NAME) .

train:
	docker run --rm \
		-v "$(CURDIR)/data:/app/data" \
		-v "$(CURDIR)/model:/app/model" \
		$(IMAGE_NAME) \
		train.py \
		--train-csv /app/$(TRAIN_CSV) \
		--model-out /app/$(MODEL_PATH) \
		--features-out /app/$(FEATURES_PATH)

predict:
	docker run --rm \
		-v "$(CURDIR)/data:/app/data" \
		-v "$(CURDIR)/model:/app/model" \
		-v "$(CURDIR)/output:/app/output" \
		$(IMAGE_NAME) \
		predict.py \
		--input-csv /app/$(INPUT_CSV) \
		--output-csv /app/$(PREDICTIONS_CSV) \
		--model-path /app/$(MODEL_PATH) \
		--features-path /app/$(FEATURES_PATH)

shell:
	docker run --rm -it \
		-v "$(CURDIR)/data:/app/data" \
		-v "$(CURDIR)/model:/app/model" \
		-v "$(CURDIR)/output:/app/output" \
		--entrypoint /bin/bash \
		$(IMAGE_NAME)

compose-build:
	podman compose build

compose-train:
	podman compose run --rm taxi \
		train.py \
		--train-csv /app/$(TRAIN_CSV) \
		--model-out /app/$(MODEL_PATH) \
		--features-out /app/$(FEATURES_PATH)

compose-predict:
	podman compose run --rm taxi \
		predict.py \
		--input-csv /app/$(INPUT_CSV) \
		--output-csv /app/$(PREDICTIONS_CSV) \
		--model-path /app/$(MODEL_PATH) \
		--features-path /app/$(FEATURES_PATH)
