.PHONY: default
default: install

.PHONY: build
build:
	rm -rf dist/ build/
	python -m pip install build
	python -m build .

.PHONY: clean
clean:
	-rm -f dist/openai-*.tar.gz
	find . -name '*.pyc' -delete

.PHONY: spotless
spotless: clean
	find . -name '__pycache__' -delete

.PHONY: install
install: clean build
	python -m pip install -U dist/openai-*.tar.gz

.PHONY: upload
upload:
	python -m pip install twine
	python -m twine upload dist/openai-*
	rm -rf dist
