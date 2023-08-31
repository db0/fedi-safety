FROM docker.io/python:3.10-slim-bookworm

WORKDIR /app
COPY lemmy_safety lemmy_safety
COPY lemmy_safety_local_storage.py lemmy_safety_local_storage.py
COPY lemmy_safety_object_storage.py lemmy_safety_object_storage.py
COPY requirements.txt requirements.txt

ENV PYTHONPATH='/app'
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python3.10" ]
