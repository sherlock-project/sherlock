FROM python:3.7-alpine as build
RUN apk add --no-cache linux-headers g++ gcc libxml2-dev libxml2 libxslt-dev
COPY requirements.txt /opt/sherlock/
WORKDIR /wheels
RUN pip3 wheel -r /opt/sherlock/requirements.txt

FROM python:3.7-alpine
COPY --from=build /wheels /wheels
COPY . /opt/sherlock/
WORKDIR /opt/sherlock
RUN pip3 install -r requirements.txt -f /wheels \
  && rm -rf /wheels \
  && rm -rf /root/.cache/pip/*

ARG VCS_REF
ARG VCS_URL="https://github.com/sherlock-project/sherlock"
LABEL org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL

ENTRYPOINT ["python", "sherlock.py"]
