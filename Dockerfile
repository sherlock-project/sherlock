FROM python:3.7-slim-bullseye as build

RUN pip3 install poetry
COPY . .
RUN poetry build

FROM python:3.7-slim-bullseye

ARG VCS_REF
ARG VCS_URL="https://github.com/sherlock-project/sherlock"

LABEL org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL

COPY --from=build dist/*.whl dist/
RUN pip3 install dist/*.whl && rm -rf dist

ENTRYPOINT ["sherlock"]
