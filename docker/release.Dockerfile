FROM python:3.13-bullseye AS build-linux
WORKDIR /workdir
RUN pip install poetry
COPY . .
RUN --mount=type=secret,id=env_file set -a \
    && . /run/secrets/env_file \
    && set +a \
    && poetry config repositories.devkit https://github.com/A-2-4-8-5-10-9-7-3-6-1/python-devkit.git \
    && poetry install
RUN poetry run pyinstaller pyinstaller.spec
RUN poetry build

FROM scottyhardy/docker-wine AS build-windows
ENV PYTHON_FOLDER=%LOCALAPPDATA%\\Programs\\Python\\Python313
WORKDIR /workdir
RUN apt update \
    && apt install -y xvfb
RUN wget -O python-3.13.1.exe https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe
RUN xvfb-run wine python-3.13.1.exe /quiet
RUN wine cmd /c "${PYTHON_FOLDER}\python.exe" -m pip install poetry
COPY . .
RUN --mount=type=secret,id=env_file set -a \
    && . /run/secrets/env_file \
    && set +a \
    && wine cmd /c " \
    set PATH=%PATH%${PYTHON_FOLDER};${PYTHON_FOLDER}/Scripts; \
    && poetry config repositories.devkit https://github.com/A-2-4-8-5-10-9-7-3-6-1/python-devkit.git \
    && poetry install \
    "
RUN wine cmd /c " \
    set PATH=%PATH%${PYTHON_FOLDER};${PYTHON_FOLDER}/Scripts; \
    && poetry run pyinstaller pyinstaller.spec \
    "

FROM ubuntu
WORKDIR /workdir
COPY --from=build-linux /workdir/dist/ ./
COPY --from=build-windows /workdir/dist/ ./
ENTRYPOINT [ "cp", "-r", ".", "/output" ]
