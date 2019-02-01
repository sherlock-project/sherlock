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

ENTRYPOINT ["python", "sherlock.py"]
