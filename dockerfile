# ==== Development Environment ====

FROM python:3.13-slim-bullseye AS development
ENV HADOLINT_SHA256=56de6d5e5ec427e17b74fa48d51271c7fc0d61244bf5c90e828aab8362d55010
ENV NODESOURCE_SHA256=dd3bc508520fcdfdc8c4360902eac90cba411a7e59189a80fb61fcbea8f4199c
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN set -e; \
    apt-get update; \
    apt-get install --no-install-recommends -y git=1:2.30.2-1+deb11u4 curl=7.74.0-1.3+deb11u14; \
    curl -fSL -o /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64; \
    echo "${HADOLINT_SHA256} /usr/local/bin/hadolint" | sha256sum -c -; \
    chmod +x /usr/local/bin/hadolint; \
    curl -fSL -o /tmp/nodesource_setup.sh https://deb.nodesource.com/setup_20.x; \
    echo "${NODESOURCE_SHA256} /tmp/nodesource_setup.sh" | sha256sum -c -; \
    chmod +x /tmp/nodesource_setup.sh; \
    /tmp/nodesource_setup.sh; \
    rm -rf /tmp/nodesource_setup.sh; \
    apt-get install --no-install-recommends -y nodejs=20.18.3-1nodesource1; \
    rm -rf /var/lib/apt/lists/*; \
    pip install --no-cache-dir poetry==2.1.1; \
    useradd -m developer -s /bin/bash;
USER developer
ENTRYPOINT [ "/bin/bash" ]
