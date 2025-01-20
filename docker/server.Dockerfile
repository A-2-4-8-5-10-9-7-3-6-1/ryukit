FROM python:3.13-bullseye AS poetry
RUN pip install poetry

FROM poetry
ARG port=8000
ARG content_location
EXPOSE ${port}
ENV RYUJINXKIT_CONTENT=${content_location}
WORKDIR /workdir
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry install && poetry run gunicorn -b 0.0.0.0:${port} ryujinxkit_server.constants.server:APP" ]
