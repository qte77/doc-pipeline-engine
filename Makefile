.SILENT:
.ONESHELL:
.PHONY: \
	install install-models install-image-ocr install-v2-nlp \
	setup-uv setup-dev setup-claude-code setup-npm-tools setup-lychee \
	test test-contracts test-rerun test-fix-snapshots \
	lint lint-md lint-links validate clean help
.DEFAULT_GOAL := help

VERBOSE ?=
ifndef VERBOSE
  RUFF_QUIET := --quiet
  PYTEST_QUIET := -q --tb=short --no-header
endif


# MARK: SETUP


install:  ## Install dev deps (uv sync)
	uv sync

setup-uv:  ## Bootstrap uv + frozen deps (devcontainer onCreateCommand)
	pip install -q uv
	uv sync --frozen

setup-dev:  ## Full dev env: uv sync + claude-code + npm tools + lychee (devcontainer postCreateCommand)
	uv sync
	$(MAKE) -s setup-claude-code
	$(MAKE) -s setup-npm-tools
	$(MAKE) -s setup-lychee

setup-claude-code:  ## Install Claude Code CLI
	if command -v claude > /dev/null 2>&1; then
		echo "claude already installed: $$(claude --version)"
	else
		curl -fsSL https://claude.ai/install.sh | bash
		echo "claude installed: $$(claude --version)"
	fi

setup-npm-tools:  ## Install npm-based dev tools (markdownlint)
	npm install -gs markdownlint-cli
	echo "markdownlint version: $$(markdownlint --version)"

setup-lychee:  ## Install lychee link checker (Rust binary, requires sudo)
	if command -v lychee > /dev/null 2>&1; then
		echo "lychee already installed: $$(lychee --version)"
	else
		curl -sL https://github.com/lycheeverse/lychee/releases/latest/download/lychee-x86_64-unknown-linux-gnu.tar.gz \
			| sudo tar xz -C /usr/local/bin lychee
		echo "lychee installed: $$(lychee --version)"
	fi

install-image-ocr:  ## Use case: extract image samples — installs Tesseract + eng (system pkg)
	if command -v apt-get > /dev/null 2>&1; then
		sudo apt-get update -qq && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
	elif command -v dnf > /dev/null 2>&1; then
		sudo dnf install -y tesseract tesseract-langpack-eng
	else
		echo "Unsupported package manager. Install tesseract-ocr + eng traineddata manually."
		exit 1
	fi
	tesseract --list-langs

install-v2-nlp:  ## Use case: V2 leg with NER entities — installs spaCy extra + en_core_web_sm
	uv sync --extra v2
	uv run python -m spacy download en_core_web_sm

install-models: install-v2-nlp  ## Deprecated alias for install-v2-nlp; will be removed in §0.5.0


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
