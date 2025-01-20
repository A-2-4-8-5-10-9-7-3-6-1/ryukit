FROM python:3.13-bullseye AS poetry
RUN pip install poetry

FROM poetry
ENV RYUJINXKIT_CONTENT=ryujinxkit-server/content.tar.gz
ENV RYUJINXKIT_PORT=8000
EXPOSE ${RYUJINXKIT_PORT}
WORKDIR /workdir
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry install && poetry run gunicorn -b 0.0.0.0:${RYUJINXKIT_PORT} ryujinxkit_server.constants.server:APP" ]
