import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
AUDIO_VAULT_DIR = STORAGE_DIR / "audio_vault"
VOICE_PROFILES_DIR = STORAGE_DIR / "voice_profiles"

# Ensure directories exist
for directory in [DATA_DIR, STORAGE_DIR, AUDIO_VAULT_DIR, VOICE_PROFILES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "kathai.db"
SERVER_HOST = os.environ.get("KATHAI_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("KATHAI_PORT", "8000"))
