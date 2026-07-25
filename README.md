# JanSathi AI - Public Assistance & Citizen Services Portal

An accessible, citizen-first public service portal built to provide guidance, scheme recommendations, reminders, and support for civic services powered by Sarvam AI and WhatsApp Cloud API integration.

## Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Router DOM, Lucide React
- **Backend**: Python FastAPI, Uvicorn, Pydantic, SQLAlchemy
- **AI & Integrations**: Sarvam AI API, WhatsApp Cloud API
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
│   │   ├── main.py         # FastAPI app creation, CORS middleware & startup diagnostics
│   │   ├── config.py       # Pydantic settings configuration
│   │   ├── database.py     # SQLite connection & session generator
│   │   ├── seed.py         # Seed database with government schemes & sample citizen
│   │   ├── routers/        # Health, Citizens, Schemes, Reminders, Assistant, Webhook
│   │   ├── services/       # AI Case Worker, Sarvam AI, WhatsApp Cloud API service
│   │   ├── models/         # SQLAlchemy Database models (Citizen, Scheme, Reminder)
│   │   ├── schemas/        # Pydantic validation schemas
│   │   └── utils/          # Helper utilities
│   ├── main.py             # Uvicorn launcher
│   └── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Activate virtualenv:
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# Configure environment variables in backend/.env:
# SARVAM_API_KEY=sk_...
# WHATSAPP_ACCESS_TOKEN=...
# WHATSAPP_PHONE_NUMBER_ID=...
# WHATSAPP_VERIFY_TOKEN=...

python main.py
```
The FastAPI application will start on `http://localhost:8000`.
- API Health Check: `http://localhost:8000/health`
- Interactive API Docs: `http://localhost:8000/docs`
- WhatsApp Webhook Endpoint: `http://localhost:8000/webhook`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend application will start on `http://localhost:5173`.

---

## Key Features

- **Indian Public-Service Visual Theme**: Saffron, Navy, and Emerald Green palette, high contrast, accessible typography.
- **AI Case Worker**:
  - Structured citizen info extraction (income, age, occupation, gender, state, district, needs).
  - Missing field detection with targeted follow-up question.
  - SQLite grounded government scheme matching (Scholarships, Agriculture/Farmers, Women Welfare, Senior Citizens, Health).
- **Sarvam AI Integration**: Dedicated client with fallback rule engine if API credentials are not set.
- **WhatsApp Cloud API Integration**:
  - `GET /webhook` verification handler.
  - `POST /webhook` for parsing incoming messages, marking as read, querying AI case worker, and replying to citizens via WhatsApp.
  - Graceful isolation: Backend runs smoothly even when WhatsApp credentials are omitted.
