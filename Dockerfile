FROM python:3.13-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=utf-8
ENV DEBUG false

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
ADD . /code
ENTRYPOINT ["bash", "entrypoint.sh"]