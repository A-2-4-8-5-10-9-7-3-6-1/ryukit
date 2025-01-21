FROM python:3.13-bullseye AS poetry
RUN pip install poetry

FROM poetry
ARG port=8000
EXPOSE ${port}
ENV PORT=${port}
WORKDIR /workdir
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry install && poetry run gunicorn -b 0.0.0.0:${PORT} ryujinxkit_server.constants.server:APP" ]
