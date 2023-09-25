FROM docker.io/python:3.10-slim-bookworm
MAINTAINER @penguincoder:hive.beehaw.org
LABEL org.opencontainers.image.source https://github.com/db0/fedi-safety

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY ["*.py", "requirements.txt", "/app/"]
ADD fedi_safety /app/fedi_safety

RUN <<EOF
    set -eu
    apt-get -qq update
    apt-get -qq upgrade
    apt-get -qq install --no-install-recommends dumb-init curl > /dev/null
    apt-get -qq autoremove
    apt-get clean
    python3.10 -m pip install --no-cache-dir -r requirements.txt
    python3.10 /app/lemmy_safety_pictrs.py || (exit 0)
EOF

ENV PYTHONPATH="/app"
ENTRYPOINT [ "/usr/bin/dumb-init", "--" ]
STOPSIGNAL SIGINT
CMD ["python3.10", "/app/lemmy_safety_pictrs.py"]
