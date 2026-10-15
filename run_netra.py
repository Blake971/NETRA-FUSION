"""Start the merged local NETRA Fusion workspace: python run_netra.py."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.runtime'))
sys.path.insert(0, str(ROOT / 'netra - Copy' / 'backend'))

# Configure API keys
os.environ['LEAK_LOOKUP_API_KEY'] = 'cf6934946329a7ca33b94535d28f8e09'
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', '')
os.environ['GEMINI_MODEL'] = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')

if __name__ == '__main__':
    try:
        import uvicorn
    except ImportError:
        raise SystemExit('Install dependencies first: python -m pip install --target .runtime -r "netra - Copy/backend/fusion_requirements.txt"')
    print('NETRA Fusion: http://127.0.0.1:8001 | Press Ctrl+C to stop.')
    print('Gemini AI is enabled only when GEMINI_API_KEY is provided in the environment.')
    print('Leak-Lookup API is configured for email breach checking.')
    uvicorn.run('fusion_api:app', host='127.0.0.1', port=8001)
