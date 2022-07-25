FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER root
WORKDIR /code

RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools
COPY requirements.txt /code/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /code/etl
COPY . /code/etl

ENV PYTHONPATH "${PYTHONPATH}:/code/etl"
