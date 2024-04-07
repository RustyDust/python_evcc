# Makefile ;)

dist: clean
	python -m build
	twine check dist/*

push:
	twine upload dist/*

all: dist push

clean:
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
	rm -rf build
	rm -rf dist
	rm -rf evcc/*.egg-info

.phony: dist
