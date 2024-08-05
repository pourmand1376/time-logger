ifeq ($(shell which conda),)
    CONDA_ACTIVATE =
else
    CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
endif

.PHONY: help
help:
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-30s\033[0m %s\n", $$1, $$2}'


.PHONY: test
test:
	$(CONDA_ACTIVATE)
	pytest tests/

run: 
	$(CONDA_ACTIVATE)
	python run_examples.py

clean: ## cleans generated files
	rm -rf .pytest_cache
	rm -rf .aider.tags*
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf tests/__pycache__

publish_to_pip: clean ## publish this package to pip
	$(CONDA_ACTIVATE)
	pip install --upgrade build twine
	python -m build
	python -m twine upload dist/*

publish_to_pypi_test: clean ## publish this package to pypi
	$(CONDA_ACTIVATE)
	pip install --upgrade build twine
	python -m build
	python -m twine upload --repository testpypi dist/*