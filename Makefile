test:
	( cd tests && bash run-tests.sh )
docker-build:
	docker build -t http-log-monitoring:latest .
docker-run:
	docker run -t --rm http-log-monitoring:latest /bin/bash -c 'make test'
