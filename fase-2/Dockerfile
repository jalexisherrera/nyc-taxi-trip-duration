FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train.py predict.py ./

RUN mkdir -p /app/data /app/model /app/output

# Los datos y modelos se montan por volumen desde el host.
VOLUME ["/app/data", "/app/model", "/app/output"]

ENTRYPOINT ["python"]
CMD ["train.py", "--help"]
