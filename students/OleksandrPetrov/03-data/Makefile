
# Self-Documented Makefile approach, borrowed from: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


py.setup:  ## Configure Python
	@pip install --upgrade setuptools pip wheel twine pipenv awscli


env.setup:  ## Make Python pipenv environment
	@echo "Making runtime environment..."
	-@pipenv --rm
	@pipenv sync --bare --dev
	@pipenv lock --requirements > python.packages.txt
	@mkdir -p wikidumps
	@cd wikidumps && python download.py


codestyle:  ## Check Python sources for PEP8 compliance
	@echo "Checking Python sources for PEP8 compliance..."
	@pipenv run pycodestyle wikidumps/*.py --ignore=E501,W503
	@pipenv run pycodestyle *.py --ignore=E501,W503


run.all:  ## Run all tasks
	@echo "Running tasks..."
	@pipenv run python 1.wiktionary.py
	@pipenv run python 3.agreement.py
