FROM python:latest
LABEL maintainer="mortolian"

RUN mkdir -p /app
WORKDIR /app
VOLUME [ "/app" ]

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]