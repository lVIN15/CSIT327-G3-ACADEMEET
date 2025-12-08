# ...existing code...
import os
from typing import Optional
from dotenv import load_dotenv

# Load local .env only if explicitly allowed (mirrors settings.py behavior)
if os.getenv("USE_ENV_FILE", "0").lower() in ("1", "true", "yes"):
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)

# Read credentials from environment variables
SUPABASE_URL = os.getenv("https://imbbllwwyungzmanpwra.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltYmJsbHd3eXVuZ3ptYW5wd3JhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MTMwNzEsImV4cCI6MjA3Njk4OTA3MX0.OlctzzKxgasDSIAtBHNkbSSGt-0Z-XZ20eu3YDH-Pqs")

_supabase_client: Optional[object] = None

def get_supabase_client():
    """Return a cached Supabase client, creating it on first use.

    Lazy-imports the supabase package to avoid import-time failures during
    Django system checks when the package isn't installed.
    """
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment.")
        try:
            from supabase import create_client  # local import to avoid ModuleNotFoundError at import time
        except Exception as e:
            raise RuntimeError("Missing 'supabase' package. Install with: python -m pip install supabase") from e
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def get_holidays(year=None, month=None):
    """Fetch holidays from Supabase"""
    try:
        sb = get_supabase_client()
        query = sb.table('holidays').select('*')

        if year is not None and month is not None:
            y = int(year)
            m = int(month)
            start_date = f"{y}-{m:02d}-01"
            if m == 12:
                end_date = f"{y + 1}-01-01"
            else:
                end_date = f"{y}-{m + 1:02d}-01"
            query = query.gte('date', start_date).lt('date', end_date)

        response = query.execute()
        return getattr(response, "data", response)
    except Exception as e:
        print(f"Error fetching holidays: {e}")
        return []

def get_professors():
    """Fetch professors from Supabase"""
    try:
        sb = get_supabase_client()
        response = sb.table('professors').select('*').execute()
        return getattr(response, "data", response)
    except Exception as e:
        print(f"Error fetching professors: {e}")
        return []

def get_schedules():
    """Fetch schedules from Supabase"""
    try:
        sb = get_supabase_client()
        response = sb.table('schedules').select('*').execute()
        return getattr(response, "data", response)
    except Exception as e:
        print(f"Error fetching schedules: {e}")
        return []
# ...existing code...