FROM docker.io/python:3.10-slim-bookworm

WORKDIR /app
COPY fedi_safety fedi_safety
COPY *.py .
COPY requirements.txt requirements.txt

ENV PYTHONPATH='/app'
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python3.10" ]
