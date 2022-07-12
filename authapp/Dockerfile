FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools 
COPY requirements.txt /code/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /code/app
COPY . /code/app

ENV PYTHONPATH "${PYTHONPATH}:/code/app"

CMD uwsgi --master \
  --single-interpreter \
  --workers $WORKERS \
  --gevent $ASYNC_CORES \
  --protocol $PROTOCOL \
  --socket 0.0.0.0:$APP_PORT \
  --module wsgi_app:app