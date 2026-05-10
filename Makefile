.PHONY: dev backend frontend install

dev:
	@echo "Starting backend + frontend..."
	@make -j2 backend frontend

backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

install:
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
