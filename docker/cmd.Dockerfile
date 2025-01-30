FROM python:3.13-bullseye AS build-linux
WORKDIR /workdir
RUN pip install poetry
COPY . .
RUN poetry build
RUN --mount=type=secret,id=env_file \
    set -a \
    && . /run/secrets/env_file \
    && set +a \
    && cat /run/secrets/env_file \
    && poetry install \
    && poetry run pyinstaller pyinstaller.spec

FROM ubuntu AS build-windows
WORKDIR /workdir
RUN dpkg --add-architecture i386
RUN apt update \
    && apt install -y wine curl xvfb wine32 
RUN curl -o python-installer.exe https://www.python.org/ftp/python/3.13.1/python-3.13.1.exe
RUN xvfb-run wine python-installer.exe /quiet
RUN wine pip install poetry
COPY . .
RUN --mount=type=secret,id=env_file \
    set -a \
    && . /run/secrets/env_file \
    && set +a \
    && wine poetry install \
    && poetry run pyinstaller pyinstaller.spec

FROM ubuntu
WORKDIR /workdir
COPY --from=build-linux /workdir/dist/ ./dist
COPY --from=build-windows /workdir/dist/ ./dist
