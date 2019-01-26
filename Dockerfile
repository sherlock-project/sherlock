FROM python:3.7-alpine
RUN /sbin/apk add tor
COPY . /opt/sherlock/
RUN /usr/local/bin/pip install -r /opt/sherlock/requirements.txt

ENTRYPOINT ["python", "/opt/sherlock/sherlock"]