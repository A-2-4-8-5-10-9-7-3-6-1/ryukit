# ------------------
# Poetry Environment
# ------------------
FROM python:3.13-slim-bullseye AS poetry
RUN pip install --no-cache-dir poetry==2.1.1

# -----------------------
# Development Environment
# -----------------------
FROM poetry AS development
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
    && apt-get install --no-install-recommends -y git=1:2.30.2-1+deb11u4 curl=7.74.0-1.3+deb11u14 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash \
    && apt-get install --no-install-recommends -y nodejs=20.18.3-1nodesource1 \
    && rm -rf /var/lib/apt/lists/*