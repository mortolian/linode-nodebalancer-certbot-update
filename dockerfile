FROM python:latest
LABEL maintainer="mortolian"

RUN mkdir -p /app
WORKDIR /app
VOLUME [ "/app" ]

RUN pip3 install python-dotenv

ENTRYPOINT [ "python", "main.py" ]