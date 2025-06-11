FROM ubuntu:25.10@sha256:dd397d3b5e4896054db111cb5145c0c08a6e7a669537e750e79e0385f2d69207 AS development
SHELL [ "bash", "-o", "pipefail", "-c" ]
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    ca-certificates=20250419 \
    curl=8.13.0-5ubuntu1 \
    git=1:2.48.1-0ubuntu1 && \
    { \
    curl -LsSf https://astral.sh/uv/0.7.12/install.sh | sh & \
    curl -fsSL https://deb.nodesource.com/setup_24.x | sh & \
    wait; \
    } && \
    mv \
    ~/.local/bin/uv \
    ~/.local/bin/uvx \
    /usr/local/bin && \
    apt-get -y install --no-install-recommends \
    nodejs=24.1.0-1nodesource1 && \
    apt-get -y purge \
    curl && \
    apt-get -y autoremove && \
    rm -r \
    /var/lib/apt/lists/* && \
    useradd -ms /bin/bash dev
USER dev
WORKDIR /project
VOLUME [ "/project" ]
ENTRYPOINT [ "/bin/bash" ]
