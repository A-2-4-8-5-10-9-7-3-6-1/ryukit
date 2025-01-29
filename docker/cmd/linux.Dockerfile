FROM python:3.13-bullseye AS poetry
RUN pip install poetry
ARG python_devkit_pat
ARG python_devkit_username
RUN poetry config http-basic.python-devkit ${python_devkit_username} ${python_devkit_pat}

FROM poetry
WORKDIR /workdir
COPY . .
ENTRYPOINT [ "/bin/bash", "-c", "poetry build && poetry install && poetry run pyinstaller pyinstaller.spec" ]
