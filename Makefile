.PHONY: activate run plus

activate:
	source .venv/bin/activate

run:
	python3 main.py

plus:
	open -n -a "/Applications/SurfTank.app"