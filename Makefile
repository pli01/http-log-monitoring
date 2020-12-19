format:
	autopep8 -d  --exit-code *.py || autopep8 -i  --exit-code *.py
test:
	( cd tests && bash run-tests.sh )
docker-build:
	docker-compose build --force-rm http-log-monitoring
docker-run-test:
	docker-compose run --rm -T --entrypoint /bin/bash  http-log-monitoring -c 'make test'
	docker-compose down -v || true
docker-stack-run:
	docker-compose up
	docker-compose down -v || true
docker-stack-down:
	docker-compose down -v || true
