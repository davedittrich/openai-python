.PHONY: default
default: install

.PHONY: build
build:
	python setup.py sdist

.PHONY: clean
clean:
	-rm -f dist/openai-*.tar.gz

.PHONY: install
install: clean build
	python -m pip install -U dist/openai-*.tar.gz

.PHONY: upload
upload:
	twine upload dist/openai-*.tar.gz
	rm dist/openai-*.tar.gz

