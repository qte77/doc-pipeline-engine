.PHONY: help install test test-contracts test-failure test-policy-local-only happy-path orch-bench-dryrun lint clean

help:
	@echo "make install                  - install dev deps (pip install -e '.[dev]')"
	@echo "make test                     - run full test suite"
	@echo "make test-contracts           - JSON schema round-trip tests"
	@echo "make happy-path               - E2E on samples/generic/sample.pdf via P1"
	@echo "make test-failure             - F1, F2, F4, F5, F11, F12 failure tests"
	@echo "make test-policy-local-only   - verify local-only policy blocks outbound calls"
	@echo "make orch-bench-dryrun        - dry-run the P1..P4 orchestration feasibility harness"
	@echo "make lint                     - ruff check"
	@echo "make clean                    - remove caches + release/"

install:
	pip install -e ".[dev]"

test:
	pytest

test-contracts:
	pytest tests/test_contracts.py -v

happy-path:
	pytest tests/test_happy_path.py -v

test-failure:
	pytest tests/test_failure_paths.py -v

test-policy-local-only:
	pytest tests/test_failure_paths.py::test_F5_policy_violation_local_only -v

orch-bench-dryrun:
	@for p in p1 p2 p3 p4; do \
	  echo "=== $$p dry-run ==="; \
	  python eval/orchestration-bench/run_$$p.py --dry-run; \
	done

lint:
	ruff check .

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ **/__pycache__ release/
	find . -name "*.pyc" -delete
