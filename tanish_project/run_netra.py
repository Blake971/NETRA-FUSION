"""Start the merged local NETRA Fusion workspace: python run_netra.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.runtime'))
sys.path.insert(0, str(ROOT / 'netra - Copy' / 'backend'))

if __name__ == '__main__':
    try:
        import uvicorn
        import fastapi
        import dns.resolver
    except ImportError:
        raise SystemExit('Install dependencies first: python -m pip install --target .runtime -r "netra - Copy/backend/fusion_requirements.txt"')
    if not (ROOT / 'netra - Copy/frontend/dist/index.html').exists():
        raise SystemExit('Frontend missing. Run npm run build in netra - Copy/frontend.')
    if '--check' in sys.argv:
        import fusion_api
        with fusion_api.connection() as db:
            db.execute('SELECT 1').fetchone()
        print('Ready: Python dependencies, frontend build and local database are available.')
        raise SystemExit(0)
    print('NETRA Fusion: http://127.0.0.1:8001 | Press Ctrl+C to stop.')
    uvicorn.run('fusion_api:app', host='127.0.0.1', port=8001)
