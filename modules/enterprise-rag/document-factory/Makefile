.PHONY: test plan-gold plan-scale dry-run status-gold

test:
	python -m pytest -q

plan-gold:
	python -m src.cli plan --corpus gold --n 500 --seed 47

plan-scale:
	python -m src.cli plan --corpus scale --n 10000 --seed 47

dry-run:
	python -m src.cli generate --corpus gold --limit 10 --dry-run

status-gold:
	python -m src.cli status --corpus gold
