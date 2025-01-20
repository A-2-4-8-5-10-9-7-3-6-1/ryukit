FROM python:3.13-bullseye AS poetry
WORKDIR /workdir
RUN pip install poetry

FROM poetry AS package
COPY . .
ENTRYPOINT [ "python", "-m", "poetry", "build" ]

FROM poetry AS app
RUN python -m poetry install
ENTRYPOINT [ "python", "-m", "poetry", "run", "pyinstaller", "resources/configs/pyinstaller.spec" ]

FROM alpine:latest
COPY --from=package dist/ ./dist
COPY --from=app dist/ ./dist
