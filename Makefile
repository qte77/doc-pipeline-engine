.SILENT:
.ONESHELL:
.PHONY: \
	install install_models install_image_ocr install_local_nlp install_v2_nlp \
	setup_uv setup_dev setup_claude_code setup_npm_tools setup_lychee \
	test test_contracts test_rerun test_fix_snapshots \
	lint lint_md lint_links validate clean help \
	docs docs_serve docs_index docs_contracts
.DEFAULT_GOAL := help

VERBOSE ?=
ifndef VERBOSE
  RUFF_QUIET := --quiet
  PYTEST_QUIET := -q --tb=short --no-header
endif


# MARK: SETUP


install:  ## Install dev deps (uv sync)
	uv sync

setup_uv:  ## Bootstrap uv + frozen deps (devcontainer onCreateCommand)
	pip install -q uv
	uv sync --frozen

setup_dev:  ## Full dev env: uv sync + claude-code + npm tools + lychee (devcontainer postCreateCommand)
	uv sync
	$(MAKE) -s setup_claude_code
	$(MAKE) -s setup_npm_tools
	$(MAKE) -s setup_lychee

setup_claude_code:  ## Install Claude Code CLI
	if command -v claude > /dev/null 2>&1; then
		echo "claude already installed: $$(claude --version)"
	else
		curl -fsSL https://claude.ai/install.sh | bash
		echo "claude installed: $$(claude --version)"
	fi

setup_npm_tools:  ## Install npm-based dev tools (markdownlint-cli2)
	npm install -gs markdownlint-cli2
	echo "markdownlint-cli2 version: $$(markdownlint-cli2 --version)"

setup_lychee:  ## Install lychee link checker (Rust binary, requires sudo)
	if command -v lychee > /dev/null 2>&1; then
		echo "lychee already installed: $$(lychee --version)"
	else
		curl -sL https://github.com/lycheeverse/lychee/releases/latest/download/lychee-x86_64-unknown-linux-gnu.tar.gz \
			| sudo tar xz -C /usr/local/bin lychee
		echo "lychee installed: $$(lychee --version)"
	fi

install_image_ocr:  ## Use case: extract image samples — installs Tesseract + eng (system pkg)
	if command -v apt-get > /dev/null 2>&1; then
		sudo apt-get update -qq && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
	elif command -v dnf > /dev/null 2>&1; then
		sudo dnf install -y tesseract tesseract-langpack-eng
	else
		echo "Unsupported package manager. Install tesseract-ocr + eng traineddata manually."
		exit 1
	fi
	tesseract --list-langs

install_local_nlp:  ## Use case: `local` leg with NER entities — installs spaCy extra + en_core_web_sm
	uv sync --extra local
	uv run python -m spacy download en_core_web_sm

install_v2_nlp: install_local_nlp  ## Deprecated alias for install_local_nlp; will be removed in §0.5.0

install_models: install_local_nlp  ## Deprecated alias for install_local_nlp; will be removed in §0.5.0


# MARK: QUALITY


test:  ## Run full test suite
	echo "--- test$(if $(PYTEST_QUIET), [quiet])"
	uv run pytest $(PYTEST_QUIET)

test_contracts:  ## Pydantic model round-trip tests
	uv run pytest tests/test_models_round_trip.py -v

test_rerun:  ## Rerun only failed tests (use during fix iterations)
	uv run pytest --lf -x

test_fix_snapshots:  ## Run tests and auto-fix inline-snapshot expected values
	uv run pytest --inline-snapshot=fix

lint:  ## Lint Python with ruff
	echo "--- lint$(if $(RUFF_QUIET), [quiet])"
	uv run ruff check $(RUFF_QUIET) .

lint_md:  ## Lint Markdown (rules + ignores in .markdownlint-cli2.jsonc)
	echo "--- lint_md"
	if command -v markdownlint-cli2 > /dev/null 2>&1; then
		markdownlint-cli2
	else
		echo "markdownlint-cli2 not installed — run: npm install -g markdownlint-cli2"
	fi

lint_links:  ## Check links in Markdown (lychee, see lychee.toml)
	echo "--- lint_links"
	if command -v lychee > /dev/null 2>&1; then
		lychee .
	else
		echo "lychee not installed — see https://github.com/lycheeverse/lychee"
	fi

validate:  ## Pre-commit gate: lint + test + lint_md + lint_links
	set -e
	$(MAKE) -s lint
	$(MAKE) -s test
	$(MAKE) -s lint_md
	$(MAKE) -s lint_links


# MARK: DOCS


docs_contracts:  ## Regenerate docs/contracts.md from src/doc_pipeline_engine/models/
	uv run python scripts/gen_contracts_md.py
	@if ! git diff --quiet docs/contracts.md; then \
		echo "docs/contracts.md drifted from src/doc_pipeline_engine/models/ — review the diff"; \
		exit 1; \
	fi

docs_index:  ## Regenerate docs/docstrings.md (auto-generated API ref index)
	PREFIX="::: "
	find src -type f -name "*.py" -not -name "__*__*" -printf "%P\n" \
		| sed 's/\//./g' | sed 's/\.py$$//' \
		| sed "s/^/$$PREFIX/" | sort > docs/docstrings.md

docs:  ## Build the mkdocs site under site/ (uses --only-group docs)
	$(MAKE) -s docs_index
	uv run --only-group docs mkdocs build

docs_serve:  ## Live-reload mkdocs dev server (requires `uv sync --only-group docs`)
	$(MAKE) -s docs_index
	uv run --only-group docs mkdocs serve


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
