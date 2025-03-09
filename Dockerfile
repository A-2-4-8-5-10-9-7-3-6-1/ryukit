# ------------------------
# Poetry Setup Environment
# ------------------------

FROM python:3.13-bullseye
WORKDIR /workdir
RUN pip install --no-cache-dir poetry==2.1.1