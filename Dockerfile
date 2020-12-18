FROM python:3
COPY http-log-monitoring.py generate-logs.py requirements.txt Makefile tests /app/
COPY tests /app/tests/
COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
WORKDIR /app
RUN cd /app ; \
    pip install -r requirements.txt && \
    autopep8 -d  --exit-code *.py || exit $? ; \
    make test ; \
    chmod +x /docker-entrypoint.sh
ENTRYPOINT /docker-entrypoint.sh

