FROM python:3.13-bullseye AS poetry
WORKDIR /workdir
RUN pip install poetry

FROM poetry
EXPOSE 8000
ARG content_location
ENV RYUJINXKIT_CONTENT=${content_location}
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry install && poetry run gunicorn -b 0.0.0.0:8000 ryujinxkit_server.constants.server:APP" ]
