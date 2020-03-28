
# Self-Documented Makefile approach, borrowed from: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z0-9_.-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


env.setup:  ## Make Python pipenv environment
	@echo "Making runtime environment..."
	-@pipenv --rm
	@pipenv sync --bare --dev
	@pipenv run python -c "import stanza; stanza.download('uk')"
	@pipenv lock -r > python.packages.txt


codestyle:  ## Check Python sources for PEP8 compliance
	@echo "Checking Python sources for PEP8 compliance..."
	@pipenv run pycodestyle *.py --ignore=E501,W503


run.all:  ## Run all tasks
	@echo "Running tasks..."
	@pipenv run python 1.1.py > 1.1.output.txt
	@pipenv run python 2.1.headlines.py > 2.1.output.txt
	@pipenv run python 2.2.headlines.py > 2.2.output.txt
	@pipenv run python 3.1.collocations.py > 3.1.output.txt
	@pipenv run python 3.2.collocations.py > 3.2.output.txt
