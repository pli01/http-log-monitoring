FROM python:3
WORKDIR /app
COPY http-log-monitoring.py generate-logs.py requirements.txt Makefile tests /app/
COPY tests /app/tests/
RUN ( cd /app && \
      pip install -r requirements.txt && \
      autopep8 -d  --exit-code *.py && \
      make test )

