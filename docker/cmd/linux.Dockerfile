FROM python:3.13-bullseye AS poetry
WORKDIR /workdir
RUN pip install poetry

FROM poetry
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry build && poetry install && poetry run pyinstaller pyinstaller.spec" ]
