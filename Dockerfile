FROM python:3.7-slim-bullseye as build

RUN pip3 install poetry
COPY . .
RUN poetry build

FROM python:3.7-slim-bullseye

COPY --from=build dist/*.whl dist/
RUN pip3 install dist/*.whl && rm -rf dist

ENTRYPOINT ["sherlock"]
