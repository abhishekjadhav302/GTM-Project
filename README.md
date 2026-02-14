# AI GTM Enrichment System

An autonomous Go-to-Market engine that enriches company lead lists using AI and firmographic data.

# Tech Stack

- **Frontend:** React 19 + Vite + Tailwind CSS
- **Backend:** FastAPI (Python 3.12)
- **Database:** PostgreSQL (Cloud via [Neon.tech](https://neon.tech))
- **Enrichment:** [Explorium API](https://www.explorium.ai)

# Key Features

- **CSV Batch Upload:** Process 5–500 domains at once.
- **Cloud Persistence:** Data is stored in a serverless Postgres database.
- **Background Processing:** Enrichment happens in the background so the UI never freezes.
- **Real-time Updates:** Dashboard refreshes automatically as AI finds data.

# Local Setup

# 1. Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create a .env file with your DATABASE_URL from Neon.tech
uvicorn main:app --reload
```

# 2. Frontend

cd frontend
npm install
npm run dev

# Database Schema

# The companies table tracks:

domain: Unique identifier
industry: Company sector (from Explorium)
size: Employee count range
revenue: Annual revenue range

i am trying to deplaoy this project on versel
i have use Versel in my last company
