FROM ubuntu:25.10@sha256:36bbb8adc0662496d3e314bc8a25cb41c0c2e42ed25daaa07f8369d36d16f082 AS development
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN apt-get update; \
    apt-get -y install --no-install-recommends \
    curl=8.12.1-3ubuntu1 \
    git=1:2.48.1-0ubuntu1 \
    pipx=1.7.1-1; \
    pipx install --global \
    poetry==2.1.1; \
    curl -Lo /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64; \
    curl -o /usr/local/bin/nodesource https://deb.nodesource.com/setup_24.x; \
    chmod +x \
    /usr/local/bin/nodesource \
    /usr/local/bin/hadolint; \
    nodesource; \
    apt-get update; \
    apt-get -y install --no-install-recommends \
    nodejs=24.0.0-1nodesource1; \
    apt-get -y purge \
    curl; \
    apt-get -y autoremove; \
    rm -r \
    /usr/local/bin/nodesource \
    /var/lib/apt/lists/*; \
    useradd -ms /bin/bash dev
USER dev
WORKDIR /project
VOLUME [ "/project" ]
ENTRYPOINT [ "/bin/bash" ]
