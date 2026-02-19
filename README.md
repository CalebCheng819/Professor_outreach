# Professor Outreach 🎓

A simplified CRM for managing academic outreach, designed for students applying for PhDs or internships.

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Kanban Board**: Track professors by status (Draft, Sent, Replied).
- **Auto-Ingestion**: Fetch specific professor websites and extract text.
- **Card Generation**: Heuristic analysis to extract **Research Interests** and **Publications**.
- **Cold Email Generation**: Generate personalized email drafts based on extracted interests.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy (SQLite)
- **Frontend**: TypeScript, Next.js 14, Tailwind CSS v4, Radix UI
- **Processing**: `requests`, `beautifulsoup4`, `readability-lxml`

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+

### 1. Backend Setup

```bash
cd apps/api
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```
API will run at `http://localhost:8000`.

### 2. Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```
Frontend will run at `http://localhost:3000`.

## detailed Walkthrough

See [walkthrough.md](./walkthrough.md) for a step-by-step guide on how this project was built.


## Deployment 🚀

### 1. Backend (Render / Railway)
The backend is a standard FastAPI app.
1.  Create a new Web Service.
2.  Connect your GitHub repo.
3.  **Root Directory**: `apps/api`
4.  **Build Command**: `pip install -r requirements.txt`
5.  **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6.  *Copy the provided URL (e.g., `https://my-api.onrender.com`)*.

### 2. Frontend (Vercel)
The frontend is a Next.js app.
1.  Import your GitHub repo to Vercel.
2.  **Root Directory**: `apps/web`
3.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: Paste your backend URL (e.g., `https://my-api.onrender.com`)
    *   *Note: Do not add a trailing slash.*
4.  Deploy!

