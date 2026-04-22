.SILENT:
.ONESHELL:
.PHONY: install test test-contracts lint lint-md lint-links clean help
.DEFAULT_GOAL := help

VERBOSE ?=
ifndef VERBOSE
  RUFF_QUIET := --quiet
  PYTEST_QUIET := -q --tb=short --no-header
endif


# MARK: SETUP


install:  ## Install dev deps (uv sync)
	uv sync


# MARK: QUALITY


test:  ## Run full test suite
	echo "--- test$(if $(PYTEST_QUIET), [quiet])"
	uv run pytest $(PYTEST_QUIET)

test-contracts:  ## JSON schema round-trip tests
	uv run pytest tests/test_contracts.py -v

lint:  ## Lint Python with ruff
	echo "--- lint$(if $(RUFF_QUIET), [quiet])"
	uv run ruff check $(RUFF_QUIET) .

lint-md:  ## Lint Markdown (markdownlint, disable MD013)
	echo "--- lint-md"
	if command -v markdownlint > /dev/null 2>&1; then
		markdownlint '**/*.md' --ignore '.venv/**' --ignore 'samples/**' --ignore 'docs/plans/**' --disable MD013 MD060
	else
		echo "markdownlint not installed — run: npm install -g markdownlint-cli"
	fi

lint-links:  ## Check links in Markdown (lychee)
	echo "--- lint-links"
	if command -v lychee > /dev/null 2>&1; then
		lychee --exclude-path .venv --exclude-path samples .
	else
		echo "lychee not installed — see https://github.com/lycheeverse/lychee"
	fi


# MARK: CLEAN


clean:  ## Remove caches
	rm -rf .pytest_cache .ruff_cache __pycache__ **/__pycache__
	find . -name "*.pyc" -delete


# MARK: HELP


help:  ## Show available recipes
	@echo "Usage: make [recipe] [VERBOSE=1]"
	@echo ""
	@awk '/^# MARK:/ { \
		section = substr($$0, index($$0, ":")+2); \
		printf "\n\033[1m%s\033[0m\n", section \
	} \
	/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/); \
		if (helpMessage) { \
			recipe = $$1; \
			sub(/:/, "", recipe); \
			printf "  \033[36m%-22s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH) \
		} \
	}' $(MAKEFILE_LIST)
