# Imagen base Python 3.11 ligera para la API REST
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Dependencias (Flask, scikit-learn, pandas, etc.)
COPY requirements.txt .
# Instalacion de librerias sin cache de pip
RUN pip install --no-cache-dir -r requirements.txt

# Scripts compartidos con Fase 2 mas el servidor Flask
COPY train.py predict.py apirest.py ./

# Carpetas para datos, modelos y salidas montadas por volumen
RUN mkdir -p /app/data /app/model /app/output

# Puntos de montaje persistentes desde el host
VOLUME ["/app/data", "/app/model", "/app/output"]

# Puerto HTTP expuesto para la API Flask
EXPOSE 5000

# Arranque del servidor apirest.py al iniciar el contenedor
CMD ["python", "apirest.py"]
