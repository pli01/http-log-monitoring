SHELL := /bin/bash

format:
	autopep8 -d --exit-code *.py || autopep8 -i *.py

test:
	$(MAKE) -C tests

docker-build:
	docker-compose build --force-rm http-log-monitoring

docker-run-test:
	docker-compose run --rm -T --entrypoint /bin/bash http-log-monitoring -c 'make test'
	docker-compose down -v || true

docker-stack-run:
	docker-compose up
	docker-compose down -v || true
docker-stack-down:
	docker-compose down -v || true
