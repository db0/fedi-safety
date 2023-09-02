FROM docker.io/python:3.10-slim-bookworm

WORKDIR /app
COPY lemmy_safety lemmy_safety
COPY *.py .
COPY requirements.txt requirements.txt

ENV PYTHONPATH='/app'
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python3.10" ]
