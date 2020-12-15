FROM python:3
WORKDIR /app
COPY http-log-monitoring.py generate-logs.py Makefile tests /app/
COPY tests /app/tests/
RUN ( cd /app && make test )

