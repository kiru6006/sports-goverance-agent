.PHONY: run-local test-backend install-deps

install-deps:
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

run-backend:
	cd backend && source venv/bin/activate && PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

run-frontend:
	cd frontend && npm run dev

test-backend:
	cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v
