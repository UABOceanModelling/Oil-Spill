LOG ?= output.txt

.PHONY: run run-bg test install

run:
	@python app.py

# Run in the background, detached from the terminal, logging to $(LOG).
run-bg:
	@nohup python app.py > $(LOG) 2>&1 &

test:
	@python -m pytest

install:
	@pip install -e ".[dev]"
