FROM python:3.13-bullseye
ENV \
    POETRY_REPOSITORIES_DEVKIT_URL=https://github.com/A-2-4-8-5-10-9-7-3-6-1/python-devkit.git \
    POETRY_VIRTUALENVS_IN_PROJECT=true
WORKDIR /workdir
RUN pip install --no-cache-dir poetry==2.1.1
COPY . .
RUN --mount=type=secret,id=github_token \
    --mount=type=secret,id=github_username \
    "$(cat /run/secrets/github_token)" \
    && export POETRY_HTTP_BASIC_DEVKIT_PASSWORD="$?" \
    && "$(cat /run/secrets/github_username)" \
    && export POETRY_HTTP_BASIC_DEVKIT_USERNAME="$?" \
    && poetry install
RUN poetry build
ENTRYPOINT [ "cp", "-r", "dist/.", "/output" ]
