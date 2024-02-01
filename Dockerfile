FROM python:3.11-slim-bullseye as build
WORKDIR /wheels

COPY requirements.txt /opt/spectre/
RUN apt-get update \
  && apt-get install -y build-essential \
  && pip3 wheel -r /opt/spectre/requirements.txt

FROM python:3.11-slim-bullseye
WORKDIR /opt/spectre

ARG VCS_REF
ARG VCS_URL="https://github.com/spectre-project/spectre"

LABEL org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL

COPY --from=build /wheels /wheels
COPY . /opt/spectre/

RUN pip3 install --no-cache-dir -r requirements.txt -f /wheels \
  && rm -rf /wheels

WORKDIR /opt/spectre/spectre

ENTRYPOINT ["python", "spectre.py"]
