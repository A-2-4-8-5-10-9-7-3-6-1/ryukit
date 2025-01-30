FROM python:3.13-bullseye
ARG port
EXPOSE ${port}
WORKDIR /workdir
RUN pip install poetry
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry install && poetry run gunicorn -b 0.0.0.0:${port} ryujinxkit_server.constants.server:APP" ]
