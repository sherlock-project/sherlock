# Release instructions:
  # 1. Update the version tag in the Dockerfile to match the version in sherlock/__init__.py
  # 2. Update the VCS_REF tag to match the tagged version's FULL commit hash
  # 3. Build image with BOTH latest and version tags
    # i.e. `docker build -t sherlock/sherlock:0.16.0 -t sherlock/sherlock:latest .`

FROM python:3.12-slim-bullseye as build
WORKDIR /sherlock

RUN pip3 install --no-cache-dir --upgrade pip

FROM python:3.12-slim-bullseye
WORKDIR /sherlock

ARG VCS_REF= # CHANGE ME ON UPDATE
ARG VCS_URL="https://github.com/sherlock-project/sherlock"
ARG VERSION_TAG= # CHANGE ME ON UPDATE

ENV SHERLOCK_ENV=docker

LABEL org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL \
      org.label-schema.name="Sherlock" \
      org.label-schema.version=$VERSION_TAG \
      website="https://sherlockproject.xyz"

RUN pip3 install --no-cache-dir sherlock-project==$VERSION_TAG

WORKDIR /sherlock

ENTRYPOINT ["sherlock"]
