# =============================================================================

FROM python:3.13-bullseye AS poetry
WORKDIR /workdir

RUN pip install poetry

# -----------------------------------------------------------------------------

FROM poetry

COPY . .

ENTRYPOINT [ \
    "/bin/bash", \
    "-c", \
    "python -m poetry install && \
    python -m poetry run pyinstaller resources/configs/pyinstaller.spec" \
    ]

# =============================================================================
