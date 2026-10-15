# NETRA Backend

AI-Powered Digital Footprint & Security Assessment Platform - Backend API

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

## Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Mac/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Running the Server

**Development mode (with auto-reload):**
```bash
uvicorn main:app --reload --port 8000
```

**Production mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

### Health Check
- `GET /health` - Check if API is running

### Scan Operations
- `POST /scan` - Start a new domain security scan
- `GET /scan/{scan_id}` - Get scan results by ID

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── config/
│   └── settings.py      # Configuration and environment variables
├── routes/
│   ├── health.py        # Health check endpoint
│   └── scan.py          # Scan endpoints
├── scanners/
│   ├── whois.py         # WHOIS scanner module
│   ├── dns.py           # DNS scanner module
│   ├── ssl.py           # SSL scanner module
│   └── headers.py      # Security headers scanner
├── database/
│   └── database.py      # Database connection and session management
├── models/
│   └── scan.py          # Database models
└── utils/
    ├── validator.py     # Input validation utilities
    └── logger.py        # Logging utilities
```

## Development Notes

- All scanner modules return standardized JSON format
- Modules are independent and handle errors internally
- Scan continues even if individual modules fail
- Database is SQLite (can be migrated to PostgreSQL in production)

## Testing the API

### Test health endpoint
```bash
curl http://localhost:8000/health
```

### Test scan endpoint
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

## Troubleshooting

**Python not found:**
- Download and install Python 3.12 from python.org
- Add Python to your system PATH

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Port already in use:**
- Change port: `uvicorn main:app --port 8001`
- Or kill the process using port 8000

## Next Steps

1. Add Gemini API key to `.env` for AI summaries
2. Implement remaining scanner modules (CT Logs, IP Intelligence, Email Security)
3. Add database persistence for scan history
4. Implement risk engine
5. Add PDF report generation
