FROM python:3.13-bullseye
ENV RYUJINXKIT_PORT=8000
EXPOSE ${RYUJINXKIT_PORT}
WORKDIR /workdir
RUN pip install poetry
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry install && poetry run gunicorn -b 0.0.0.0:${RYUJINXKIT_PORT} ryujinxkit_server.constants.server:APP" ]
