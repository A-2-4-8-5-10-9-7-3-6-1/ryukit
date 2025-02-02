FROM python:3.13-bullseye AS build-linux
ENV POETRY_REPOSITORIES_DEVKIT_URL=https://github.com/A-2-4-8-5-10-9-7-3-6-1/python-devkit.git
WORKDIR /workdir
RUN pip install poetry
COPY . .
RUN --mount=type=secret,id=github_token \
    --mount=type=secret,id=github_username \
    export POETRY_HTTP_BASIC_DEVKIT_PASSWORD=$(cat /run/secrets/github_token) \
    && export POETRY_HTTP_BASIC_DEVKIT_USERNAME=$(cat /run/secrets/github_username) \
    && poetry install
RUN poetry run pyinstaller pyinstaller.spec

FROM scottyhardy/docker-wine AS build-windows
ENV WIN_PATH="%PATH%%LOCALAPPDATA%\Programs\Python\Python313;%LOCALAPPDATA%\Programs\Python\Python313\Scripts" \
    POETRY_REPOSITORIES_DEVKIT_URL=https://github.com/A-2-4-8-5-10-9-7-3-6-1/python-devkit.git
WORKDIR /workdir
RUN apt update \
    && apt install -y xvfb
RUN wget -O python-3.13.1.exe https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe
RUN xvfb-run wine python-3.13.1.exe /quiet
RUN wine cmd /c " \
    set PATH=${WIN_PATH} \
    && pip install poetry \
    "
COPY . .
RUN --mount=type=secret,id=github_token \
    --mount=type=secret,id=github_username \
    export POETRY_HTTP_BASIC_DEVKIT_PASSWORD=$(cat /run/secrets/github_token) \
    && export POETRY_HTTP_BASIC_DEVKIT_USERNAME=$(cat /run/secrets/github_username) \
    && wine cmd /c " \
    set PATH=${WIN_PATH} \
    && poetry install \
    "
RUN wine cmd /c " \
    set PATH=${WIN_PATH} \
    && poetry run pyinstaller pyinstaller.spec \
    "

FROM ubuntu
WORKDIR /workdir
COPY --from=build-linux /workdir/dist .
COPY --from=build-windows /workdir/dist .
ENTRYPOINT [ "cp", "-r", ".", "/output" ]
