ARG PYTHON_VERSION=3.12-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "yNNAgmpkZjNyQHXGMFzl2iBVqjl3U8fMgnfJQqV5VB6Uipa2a0"
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN apt-get update && apt-get install -y wkhtmltopdf 


EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "mnl_api.wsgi"]
