.PHONY: check
check:
	@if [ -n "$$(git ls-files '*.py')" ]; then ruff check .; else echo "no Python files"; fi
	@if [ -d tests ]; then pytest --timeout=60 -q; else echo "no tests/"; fi
	@if [ -n "$$(git ls-files '.github/workflows/*.yml')" ]; then \
		actionlint && zizmor --no-progress .github/workflows; else echo "no workflows"; fi
	python3 tools/check/check_version.py
	python3 tools/check/check_pr_form.py
	python3 tools/managed_guard.py check
	python3 tools/check/check_no_bytecode.py
	python3 tools/check/check_var_defaults.py
	bash tools/check/check_drift.sh
	@$(MAKE) --no-print-directory test-evidence

# Pull requests only: PR_BASE_REF is the base branch name (set by validate.yml); skipped when unset (local runs, pushes).
.PHONY: test-evidence
test-evidence:
	@if [ -n "$$PR_BASE_REF" ]; then python3 tools/check/check_test_evidence.py "origin/$$PR_BASE_REF"; else echo "check_test_evidence: skipped (no PR_BASE_REF)"; fi
