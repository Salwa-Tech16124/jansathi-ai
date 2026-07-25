# JanSathi AI - Public Assistance & Citizen Services Portal

An accessible, citizen-first public service portal and **Retrieval-Augmented Generation (RAG)** platform built to provide guidance, official government scheme recommendations, reminders, and support for civic services across India.

---

## 🌟 Key System Features

- **3,400+ Government Schemes Dataset**: Imported, auto-migrated, and indexed in SQLite (`jansathi.db`) with `scheme_name`, `slug`, `details`, `benefits`, `eligibility`, `application`, `documents`, `level`, `schemeCategory`, and `tags`.
- **Intelligent Retrieval & Query Normalization**:
  - Domain synonym expansion matching equivalents:
    - **Education**: `12`, `12th`, `Class XII`, `Intermediate`, `Higher Secondary`, `10th`, `SSLC`, `Scholarship`.
    - **Agriculture**: `Farmer`, `Kisan`, `Agriculture`, `Crop`, `Farming`, `Land`, `Cultivator`.
    - **Women**: `Women`, `Woman`, `Female`, `Mahila`, `Girl`, `Mother`, `Lakhpati`, `SHG`.
    - **Business**: `Business`, `MSME`, `Startup`, `Shop`, `Entrepreneur`, `Loan`.
    - **Employment**: `Job`, `Employment`, `Work`, `Skill`, `Training`, `Unemployed`, `Artisan`.
    - **Health**: `Hospital`, `Medical`, `Treatment`, `Health`, `Ayushman`, `Doctor`.
    - **Housing**: `House`, `Home`, `PMAY`, `Shelter`, `Awas`.
  - Multi-field TF-IDF style scoring returning the **Top 5** most relevant schemes.
- **Gemini 1.5 Flash RAG Grounding**:
  - Answers **ONLY** using retrieved SQLite scheme context to prevent hallucinations.
- **Official myScheme Integration**:
  - Dynamically generates verified links: `https://www.myscheme.gov.in/schemes/{slug}`.
- **Backend Conversation Memory**:
  - Remembers user context across turns (`State`, `Age`, `Gender`, `Education`, `Occupation`, `Annual Income`).
- **AI Query Intent Routing**:
  - Government scheme queries -> **SQLite Search + Gemini RAG**.
  - Greetings & casual conversation -> **Sarvam AI Service**.
- **Automated Daily Scheme Ingestion Scheduler**:
  - Non-blocking 24-hour background scheduler (`scheduler.py`) that automatically ingests newly released and upcoming 2026 government schemes into SQLite.
  - Interactive manual sync button & live status card in the **Admin Portal**.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Router DOM, Lucide React
- **Backend**: Python FastAPI, Uvicorn, Pydantic, SQLAlchemy, `google-genai` SDK
- **AI Engines**: Google Gemini 1.5 Flash (RAG Grounding) & Sarvam AI (Casual Chat)
- **Database**: SQLite (`jansathi.db`) with full B-Tree indexes on `scheme_name`, `schemeCategory`, and `tags`

---

## 📁 Project Structure

```
jansathi-ai/
├── frontend/
│   ├── src/
│   │   ├── components/     # Layout, Navbar, Footer, Toast
│   │   ├── pages/          # Landing, Chat, Reminders, Admin, NotFound
│   │   ├── services/       # API client (Axios, scheme sync, assistant chat)
│   │   ├── App.tsx         # React Router navigation
│   │   ├── main.tsx        # Application entry point
│   │   └── index.css       # Indian Public Service visual theme
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── data/
│   │   └── updated_data.csv # 3,400+ Government Schemes dataset
│   ├── app/
│   │   ├── main.py         # FastAPI app creation & background scheduler runner
│   │   ├── config.py       # Pydantic settings & env variable configuration
│   │   ├── database.py     # SQLite connection & session manager
│   │   ├── seed.py         # CSV dataset validator, de-duplicator & indexer
│   │   ├── routers/        # Health, Citizens, Schemes, Reminders, Assistant, Webhook
│   │   ├── services/       # Search Service, Gemini RAG, Sarvam AI, Collector, Scheduler
│   │   ├── models/         # SQLAlchemy models (Citizen, Scheme, Reminder)
│   │   └── schemas/        # Pydantic validation schemas
│   ├── main.py             # Uvicorn entry point
│   └── requirements.txt
└── README.md
```

---

## 🚀 Terminal Startup Instructions

### 1. Terminal 1: Start FastAPI Backend Server
```powershell
cd s:\jansathi-ai\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Terminal 2: Start React Frontend Web App
```powershell
cd s:\jansathi-ai\frontend
npm run dev
```

---

## 🌐 Application Endpoints

- **Frontend Web Portal**: [http://localhost:5173](http://localhost:5173)
- **AI Case Worker Chat**: [http://localhost:5173/chat](http://localhost:5173/chat)
- **Admin Portal & Scheme Sync**: [http://localhost:5173/admin](http://localhost:5173/admin)
- **FastAPI Health Status**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
