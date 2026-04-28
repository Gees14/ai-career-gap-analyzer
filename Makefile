.PHONY: install-backend install-frontend run-backend run-frontend test docker-up docker-down clean

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

test:
	cd backend && python -m pytest tests/ -v

test-fast:
	cd backend && python -m pytest tests/ -v -k "not embedding"

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/.pytest_cache frontend/dist frontend/node_modules
