# =============================================================================

FROM python:3.13-bullseye AS poetry
WORKDIR /workdir

RUN pip install poetry

# -----------------------------------------------------------------------------

FROM poetry
ENV RYUJINXKIT_CONTENT=temp/data
EXPOSE 8000

COPY . .

RUN python -m poetry install

ENTRYPOINT [ \
    "poetry", \
    "run" , \
    "gunicorn", \
    "-b", \
    "0.0.0.0:8000", \
    "ryujinxkit_server.constants.server:APP" \
    ]

# =============================================================================
