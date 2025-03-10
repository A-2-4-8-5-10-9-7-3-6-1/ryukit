# -----------------------
# Development Environment
# -----------------------
FROM python:3.13-slim-bullseye AS development
ENV HADOLINT_SOURCE=https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64
ENV NODE_SETUP_SOURCE=https://deb.nodesource.com/setup_20.x
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && \
    apt-get install --no-install-recommends -y git=1:2.30.2-1+deb11u4 curl=7.74.0-1.3+deb11u14 \
    && curl -fsSL "${NODE_SETUP_SOURCE}" | bash \
    && apt-get install --no-install-recommends -y nodejs=20.18.3-1nodesource1 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -L -o /usr/local/bin/hadolint "${HADOLINT_SOURCE}" \
    && chmod +x /usr/local/bin/hadolint \
    && pip install --no-cache-dir poetry==2.1.1
