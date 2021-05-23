VENV_RUN = poetry run

.PHONY: test

dev-setup:
	poetry install

test:
	$(VENV_RUN) pytest
