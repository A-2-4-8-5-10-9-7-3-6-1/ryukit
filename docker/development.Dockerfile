FROM python:3.13-bullseye
WORKDIR /workdir
RUN pip install poetry
COPY . .
