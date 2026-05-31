# Imagen base Python 3.11 ligera para reducir el tamano de la imagen final
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos dependencias primero para aprovechar la cache de capas de Docker
COPY requirements.txt .
# Instalacion de librerias Python sin cache de pip
RUN pip install --no-cache-dir -r requirements.txt

# Scripts de entrenamiento y prediccion batch
COPY train.py predict.py ./

# Creacion de carpetas que se montan desde el host
RUN mkdir -p /app/data /app/model /app/output

# Puntos de montaje para datos, modelos entrenados y CSV de salida
VOLUME ["/app/data", "/app/model", "/app/output"]

# Permite ejecutar train.py o predict.py sin prefijo python en docker run
ENTRYPOINT ["python"]
# Comando por defecto: muestra la ayuda de train.py
CMD ["train.py", "--help"]
