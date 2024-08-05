.PHONY: help
help:
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-30s\033[0m %s\n", $$1, $$2}'


.PHONY: test
test:
	pytest tests/

run: 
	python run_examples.py

clean: ## cleans generated files
	rm -rf .pytest_cache
	rm -rf .aider.tags*
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf tests/__pycache__

publish_to_pip: clean ## publish this package to pip
	python3 -m pip install --upgrade build twine
	python3 -m build
	python -m twine upload dist/*

publish_to_pypi_test: clean ## publish this package to pypi
	python3 -m pip install --upgrade build twine
	python3 -m build
	python3 -m twine upload --repository testpypi dist/*