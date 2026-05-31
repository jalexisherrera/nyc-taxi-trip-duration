FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py predict.py apirest.py ./

RUN mkdir -p /app/data /app/model /app/output

VOLUME ["/app/data", "/app/model", "/app/output"]

EXPOSE 5000

CMD ["python", "apirest.py"]
