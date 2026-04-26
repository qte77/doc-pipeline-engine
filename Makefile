.SILENT:
.ONESHELL:
.PHONY: install install-models test test-contracts test-rerun test-fix-snapshots lint lint-md lint-links validate clean help
.DEFAULT_GOAL := help

VERBOSE ?=
ifndef VERBOSE
  RUFF_QUIET := --quiet
  PYTEST_QUIET := -q --tb=short --no-header
endif


# MARK: SETUP


install:  ## Install dev deps (uv sync)
	uv sync

install-models:  ## Download spaCy en_core_web_sm (~12 MB) — needs --extra v2
	uv run python -m spacy download en_core_web_sm


# MARK: QUALITY


test:  ## Run full test suite
	echo "--- test$(if $(PYTEST_QUIET), [quiet])"
	uv run pytest $(PYTEST_QUIET)

test-contracts:  ## JSON schema round-trip tests
	uv run pytest tests/test_contracts.py -v

test-rerun:  ## Rerun only failed tests (use during fix iterations)
	uv run pytest --lf -x

test-fix-snapshots:  ## Run tests and auto-fix inline-snapshot expected values
	uv run pytest --inline-snapshot=fix

lint:  ## Lint Python with ruff
	echo "--- lint$(if $(RUFF_QUIET), [quiet])"
	uv run ruff check $(RUFF_QUIET) .

lint-md:  ## Lint Markdown (markdownlint, disable MD013)
	echo "--- lint-md"
	if command -v markdownlint > /dev/null 2>&1; then
		markdownlint '**/*.md' --ignore '.venv/**' --ignore 'samples/**' --ignore 'docs/plans/**' --ignore 'outputs/**' --disable MD013
	else
		echo "markdownlint not installed — run: npm install -g markdownlint-cli"
	fi

lint-links:  ## Check links in Markdown (lychee, see lychee.toml)
	echo "--- lint-links"
	if command -v lychee > /dev/null 2>&1; then
		lychee .
	else
		echo "lychee not installed — see https://github.com/lycheeverse/lychee"
	fi

validate:  ## Pre-commit gate: lint + test + lint-md + lint-links
	set -e
	$(MAKE) -s lint
	$(MAKE) -s test
	$(MAKE) -s lint-md
	$(MAKE) -s lint-links


# MARK: CLEAN


clean:  ## Remove caches
	rm -rf .pytest_cache .ruff_cache __pycache__ **/__pycache__
	find . -name "*.pyc" -delete


# MARK: HELP


help:  ## Show available recipes
	echo "Usage: make [recipe] [VERBOSE=1]"
	echo ""
	awk '/^# MARK:/ {
		section = substr($$0, index($$0, ":")+2)
		printf "\n\033[1m%s\033[0m\n", section
	}
	/^[a-zA-Z0-9_-]+:.*?##/ {
		helpMessage = match($$0, /## (.*)/)
		if (helpMessage) {
			recipe = $$1
			sub(/:/, "", recipe)
			printf "  \033[36m%-22s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH)
		}
	}' $(MAKEFILE_LIST)
