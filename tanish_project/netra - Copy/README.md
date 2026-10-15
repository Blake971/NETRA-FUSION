# NETRA

AI-Powered Digital Footprint & Security Assessment Platform

## Overview

NETRA is a web-based cybersecurity platform that performs passive security assessments using publicly available information. It consolidates multiple security checks into a unified dashboard, calculates an overall security score, generates AI-powered explanations, and produces professional reports.

## Features

- **WHOIS Analysis** - Domain registration information
- **DNS Configuration** - Complete DNS records analysis
- **SSL Validation** - Certificate security checks
- **Security Headers** - HTTP header inspection
- **Email Security** - SPF, DKIM, DMARC verification
- **AI Reports** - Intelligent security summaries (Gemini)

## Project Structure

```
Netra/
├── docs/                    # Documentation
│   ├── 01_PROJECT_OVERVIEW.md
│   ├── 02_ARCHITECTURE.md
│   ├── 03_MODULES.md
│   ├── 04_FRONTEND.md
│   ├── 05_API_SPEC.md
│   ├── 06_DATABASE.md
│   ├── 07_AI_SPEC.md
│   ├── 08_RISK_ENGINE.md
│   ├── 09_DEVELOPMENT.md
│   └── NETRA_MASTER_CONTEXT.md
├── backend/                 # Python FastAPI backend
│   ├── main.py
│   ├── config/
│   ├── routes/
│   ├── scanners/
│   ├── database/
│   ├── models/
│   └── utils/
└── frontend/                # React frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── services/
    │   └── utils/
    └── public/
```

## Prerequisites

### Backend
- Python 3.12 or higher
- pip

### Frontend
- Node.js 18 or higher
- npm

## Installation

### 1. Install Python (if not installed)

Download and install Python 3.12 from [python.org](https://python.org)

During installation, check "Add Python to PATH"

### 2. Install Node.js (if not installed)

Download and install Node.js 18 from [nodejs.org](https://nodejs.org)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your Gemini API key
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env
```

## Running the Application

### Start Backend

```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload --port 8000
```

Backend will run at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will run at: `http://localhost:3000`

## Testing

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test Scan Endpoint
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

## Current Status

### ✅ Completed (Milestone 1: Foundation)
- Project structure
- Backend FastAPI setup
- Database connection and schema
- 4 core scanner modules (WHOIS, DNS, SSL, Headers)
- Scan controller and API endpoint
- Frontend React setup with Tailwind CSS
- Landing page

### 🚧 In Progress
- Remaining scanner modules (CT Logs, IP Intelligence, Email Security)
- Risk engine implementation
- AI integration (Gemini)
- Database persistence
- PDF report generation
- Additional frontend pages

## Documentation

For detailed specifications, see the `docs/` folder:

- `NETRA_MASTER_CONTEXT.md` - Quick reference for development
- `09_DEVELOPMENT.md` - Development workflow and milestones
- `03_MODULES.md` - Module specifications
- `05_API_SPEC.md` - API endpoint documentation

## Development Philosophy

Build vertically, not horizontally. Complete one feature end-to-end before starting the next.

## License

This is a final-year project for educational purposes.

## Support

For issues or questions, refer to the documentation in the `docs/` folder.
