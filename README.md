# School Timetable Management System

A complete School Timetable Management Web Application built with React 19, FastAPI, and PostgreSQL.

## Architecture
- **Frontend:** React, TypeScript, Vite, Tailwind CSS (shadcn/ui), TanStack Query/Table, React Hook Form, Zod, React Router, Recharts, SheetJS, Sonner.
- **Backend:** Python FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, JWT Authentication.
- **Algorithm Engine:** Constraint Satisfaction/Optimization algorithm to generate the timetable with rules like no clashes, workload balancing, teacher preferences, and substitutions.

## Getting Started

### Prerequisites
- Node.js & npm
- Python 3.10+
- PostgreSQL (or SQLite for initial development)

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
