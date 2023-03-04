.PHONY: pretty
pretty:
	poetry run black ${CURDIR}
	poetry run isort ${CURDIR} 

.PHONY: clean
clean:
	rm -rf .mypy_cache .tox dist
	find ${CURDIR} -type d -name '__pycache__' -prune -exec rm -rf "{}" \;
	find ${CURDIR} -type f -name *.pyc -delete
	rm -rf dist
