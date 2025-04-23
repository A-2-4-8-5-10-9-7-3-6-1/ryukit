# MARK: Development Environment
FROM ubuntu:25.04@sha256:79efa276fdefa2ee3911db29b0608f8c0561c347ec3f4d4139980d43b168d991 AS development
ENV POETRY_VIRTUALENVS_IN_PROJECT=true 
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN apt-get update; \
    apt-get -y install --no-install-recommends \
    curl=8.12.1-3ubuntu1 \
    git=1:2.48.1-0ubuntu1 \
    pipx=1.7.1-1; \
    pipx install --global poetry==2.1.1; \
    curl -Lo /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64; \
    curl -o /usr/local/bin/nodesource https://deb.nodesource.com/setup_20.x; \
    chmod +x \
    /usr/local/bin/nodesource \
    /usr/local/bin/hadolint; \
    nodesource; \
    apt-get -y install --no-install-recommends \
    nodejs=20.18.3-1nodesource1; \
    apt-get -y purge curl; \
    apt-get -y autoremove; \
    rm -r \
    /usr/local/bin/nodesource \
    /var/lib/apt/lists/*; \
    useradd -ms /bin/bash dev
USER dev
WORKDIR /project
VOLUME [ "/project" ]
ENTRYPOINT [ "/bin/bash" ]
