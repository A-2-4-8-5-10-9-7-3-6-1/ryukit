# =============================================================================

FROM python:3.13-bullseye AS poetry

RUN pip install pipx
RUN pipx ensurepath

RUN pipx install poetry

# -----------------------------------------------------------------------------

FROM poetry
WORKDIR /workdir

COPY . .

# =============================================================================
