FROM python:3.13-bullseye
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
WORKDIR /workdir
RUN pip install --no-cache-dir poetry==2.1.1