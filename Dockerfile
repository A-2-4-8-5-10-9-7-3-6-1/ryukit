FROM ubuntu:25.10@sha256:dd397d3b5e4896054db111cb5145c0c08a6e7a669537e750e79e0385f2d69207 AS development
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    curl=8.13.0-5ubuntu1 \
    git=1:2.48.1-0ubuntu1 \
    pipx=1.7.1-1 && \
    pipx install --global \
    poetry==2.1.1 && \
    curl -Lo /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64 && \
    curl -o /usr/local/bin/nodesource https://deb.nodesource.com/setup_24.x && \
    chmod +x \
    /usr/local/bin/nodesource \
    /usr/local/bin/hadolint && \
    nodesource && \
    apt-get update && \
    apt-get -y install --no-install-recommends \
    nodejs=24.0.0-1nodesource1 && \
    apt-get -y purge \
    curl && \
    apt-get -y autoremove && \
    rm -r \
    /usr/local/bin/nodesource \
    /var/lib/apt/lists/* && \
    useradd -ms /bin/bash dev
USER dev
WORKDIR /project
VOLUME [ "/project" ]
ENTRYPOINT [ "/bin/bash" ]
