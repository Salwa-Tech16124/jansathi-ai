# JanSathi AI - Project Foundation

An accessible, citizen-first public service portal foundation built to provide guidance, reminders, and support for civic services.

## Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Router DOM, Lucide React
- **Backend**: Python FastAPI, Uvicorn, Pydantic, SQLAlchemy
- **Database**: SQLite (`jansathi.db`)

---

## Project Structure

```
jansathi-ai/
├── frontend/
│   ├── src/
│   │   ├── components/     # Layout, Navbar, Footer
│   │   ├── pages/          # Landing, Chat, Reminders, Admin, NotFound
│   │   ├── services/       # API client (Axios)
│   │   ├── App.tsx         # React Router setup
│   │   ├── main.tsx        # Entry point
│   │   └── index.css       # Tailwind CSS & Indian Public Service theme
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app creation & CORS middleware
│   │   ├── config.py       # Pydantic settings configuration
│   │   ├── database.py     # SQLite connection & session generator
│   │   ├── routers/        # Health endpoint (GET /health)
│   │   ├── services/       # Business logic (Package)
│   │   ├── models/         # Database models (Package)
│   │   └── utils/          # Helper functions (Package)
│   ├── main.py             # Uvicorn launcher
│   └── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend application will start on `http://localhost:5173`.

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Activate virtualenv:
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python main.py
```
The FastAPI application will start on `http://localhost:8000`.
- API Health Check: `http://localhost:8000/health`
- Interactive API Docs: `http://localhost:8000/docs`

---

## Features included in Foundation
- **Indian Public-Service Visual Theme**: Saffron, Navy, and Emerald Green palette, high contrast, clean typography.
- **Frontend Routes**:
  - Landing Page (`/`)
  - AI Assistant Shell (`/chat`)
  - Citizen Reminders Shell (`/reminders`)
  - Admin Portal Placeholder (`/admin`)
  - 404 Page (`*`)
- **Backend Foundation**:
  - CORS enabled for local development.
  - `GET /health` returning `{"status": "ok"}`.
  - SQLite database engine and session dependency configured.
  - Modular package structure (`routers`, `services`, `models`, `utils`).
