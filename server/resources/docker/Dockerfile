FROM python:3.13-bullseye AS poetry
WORKDIR /workdir
RUN pip install poetry

FROM poetry
ARG content_location
RUN test -n "${content_location}" || (echo "Required argument \${content_location}." && exit 1)
ENV RYUJINXKIT_CONTENT=${content_location}
EXPOSE 8000
COPY . .
RUN python -m poetry install
ENTRYPOINT [ "python", "-m", "poetry", "run", "gunicorn", "-b", "0.0.0.0:8000", "ryujinxkit_server.constants.server:APP" ]
