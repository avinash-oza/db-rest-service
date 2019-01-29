FROM python:latest
ARG DB_REST_SERVICE_VERSION=v0.1b7

COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN mkdir -p /tmp/db-rest-service \
    && curl -SL https://github.com/avinash-oza/db-rest-service/archive/${DB_REST_SERVICE_VERSION}.tar.gz | tar xvzf - --strip-components=1 -C /tmp/db-rest-service \
    && ls -al /tmp/db-rest-service \
    && pip install -r /tmp/db-rest-service/requirements.txt \
    && pip install /tmp/db-rest-service

EXPOSE "5000"
ENTRYPOINT ["/docker-entrypoint.sh"]