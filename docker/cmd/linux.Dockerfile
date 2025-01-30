FROM python:3.13-bullseye AS poetry
RUN pip install poetry

FROM poetry
WORKDIR /workdir
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry build && poetry install && poetry run pyinstaller pyinstaller.spec" ]
