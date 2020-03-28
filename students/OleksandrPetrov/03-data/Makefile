
# Self-Documented Makefile approach, borrowed from: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


env.setup:  ## Make Python pipenv environment
	@echo "Making runtime environment..."
	-@pipenv --rm
	@pipenv sync --bare --dev
	@pipenv lock --dev --requirements > python.packages.txt


codestyle:  ## Check Python sources for PEP8 compliance
	@echo "Checking Python sources for PEP8 compliance..."
	@pipenv run pycodestyle *.py --ignore=E501,W503


run.all:  ## Run all tasks
	@echo "Running tasks..."
