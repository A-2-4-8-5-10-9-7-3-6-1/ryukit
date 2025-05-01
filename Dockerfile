# MARK: Development Environment
FROM ubuntu:25.04@sha256:79efa276fdefa2ee3911db29b0608f8c0561c347ec3f4d4139980d43b168d991 AS development
ENV POETRY_VERSION=2.1.1
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN apt-get update; \
    apt-get -y install --no-install-recommends \
    curl=8.12.1-3ubuntu1 \
    git=1:2.48.1-0ubuntu1 \
    gpg=2.4.4-2ubuntu23 \
    pipx=1.7.1-1; \
    pipx install --global poetry=="${POETRY_VERSION}"; \
    dpkg --add-architecture i386; \
    curl -Lo /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64; \
    curl -o /usr/local/bin/nodesource https://deb.nodesource.com/setup_20.x; \
    curl https://dl.winehq.org/wine-builds/winehq.key | gpg --dearmor -o /etc/apt/keyrings/winehq-archive.key -; \
    curl -o /etc/apt/sources.list.d/winehq-plucky.sources https://dl.winehq.org/wine-builds/ubuntu/dists/plucky/winehq-plucky.sources; \
    curl -o /usr/share/python_installer.exe https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe; \
    chmod +x \
    /usr/local/bin/nodesource \
    /usr/local/bin/hadolint; \
    nodesource; \
    apt-get update; \
    apt-get -y install --no-install-recommends \
    nodejs=20.19.1-1nodesource1 \
    winehq-stable=10.0.0.0~plucky-1; \
    apt-mark manual winehq-stable; \
    apt-get -y purge \
    curl; \
    apt-get -y autoremove; \
    rm -r \
    /usr/local/bin/nodesource \
    /etc/apt/keyrings/winehq-archive.key \
    /etc/apt/sources.list.d/winehq-plucky.sources \
    /var/lib/apt/lists/*; \
    useradd -ms /bin/bash dev
USER dev
WORKDIR /project
VOLUME [ "/project" ]
ENTRYPOINT [ "/bin/bash" ]
