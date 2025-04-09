# ==== Development Environment ====

FROM ubuntu:25.04@sha256:af6610ebb9372eac8cbe4e992a0cf2aeb7aa76debb5453ae705b415b3e73d7c5 AS development
ENV HADOLINT_SHA256=56de6d5e5ec427e17b74fa48d51271c7fc0d61244bf5c90e828aab8362d55010
ENV NODESOURCE_SHA256=dd3bc508520fcdfdc8c4360902eac90cba411a7e59189a80fb61fcbea8f4199c
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN set -e; \
    apt-get update; \
    apt-get install --no-install-recommends -y python3=3.13.2-2 curl=8.12.1-3ubuntu1 python3-poetry=2.1.1+dfsg-3 git=1:2.48.1-0ubuntu1; \
    curl -fSL -o /usr/local/bin/hadolint "https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64"; \
    echo "${HADOLINT_SHA256} /usr/local/bin/hadolint" | sha256sum -c -; \
    chmod +x /usr/local/bin/hadolint; \
    curl -fSL -o /usr/local/bin/nodesource https://deb.nodesource.com/setup_20.x; \
    echo "${NODESOURCE_SHA256} /usr/local/bin/nodesource" | sha256sum -c -; \
    chmod +x /usr/local/bin/nodesource; \
    nodesource; \
    rm -f /usr/local/bin/nodesource; \
    apt-get install --no-install-recommends -y nodejs=20.18.3-1nodesource1; \
    rm -rf /var/lib/apt/lists/*; \
    useradd -ms /bin/bash dev;
VOLUME [ "/project" ]
USER dev
ENTRYPOINT [ "/bin/bash" ]
