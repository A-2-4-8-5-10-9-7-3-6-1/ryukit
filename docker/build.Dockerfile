FROM python:3.13-bullseye
WORKDIR /workdir
RUN pip install --no-cache-dir poetry==2.1.1
COPY . .
ENTRYPOINT [ "poetry", "build" ]
