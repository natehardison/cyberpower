.PHONY: pretty
pretty:
	poetry run black src/cyberpower/
	poetry run isort src/cyberpower/

lint:
	poetry run flake8 src/cyberpower/

typecheck:
	poetry run mypy src/cyberpower/

.PHONY: clean
clean:
	rm -rf .mypy_cache .tox dist
	find ${CURDIR} -type d -name '__pycache__' -prune -exec rm -rf "{}" \;
	find ${CURDIR} -type f -name *.pyc -delete
	rm -rf dist
