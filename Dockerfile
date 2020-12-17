FROM python:3
WORKDIR /app
COPY http-log-monitoring.py generate-logs.py requirements.txt Makefile tests /app/
COPY tests /app/tests/
COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN if [ -z "$DISABLE_TEST" ] ; then \
      ( cd /app && \
      pip install -r requirements.txt && \
      autopep8 -d  --exit-code *.py && \
      make test ) \
    fi ; \
    chmod +x /docker-entrypoint.sh
ENTRYPOINT /docker-entrypoint.sh

