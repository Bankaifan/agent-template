.PHONY: check
check:
	python3 tools/check/check_version.py
	python3 tools/check/check_pr_form.py
	bash tools/check/check_drift.sh
