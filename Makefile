.PHONY: setup test demo dev

setup:
	python3 -m venv backend/venv
	./backend/venv/bin/pip install -r backend/requirements.txt
	./backend/venv/bin/playwright install chromium
	cd frontend && npm install

test:
	./backend/venv/bin/python -m pytest tests/

demo:
	./backend/venv/bin/python test_pipeline.py

dev:
	docker-compose up --build
