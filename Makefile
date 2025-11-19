.PHONY: install run test lint format clean docker-up docker-down

install:
	pip install -e .[dev]

run:
	@echo "Starting Simulation and HMI..."
	@trap 'kill 0' EXIT; \
	python -m simulation.modbus_server & \
	uvicorn hmi.app:app --reload --port 8000

test:
	pytest tests/

lint:
	flake8 simulation hmi attacker defender
	bandit -r simulation hmi attacker defender

format:
	black simulation hmi attacker defender tests
	isort simulation hmi attacker defender tests

clean:
	rm -rf __pycache__ .pytest_cache *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
