.PHONY: pretty
pretty:
	poetry run black .
	poetry run isort .

.PHONY: clean
clean:
	rm -rf .mypy_cache .tox dist
	find ${CURDIR} -type d -name '__pycache__' -prune -exec rm -rf "{}" \;
	find ${CURDIR} -type f -name *.pyc -delete
	rm -rf dist

.PHONY: docs
docs:
	poetry run mkdocs build
