import sqlite3
import json
from typing import Dict, Any, List, Optional
from app.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize database tables for Kathai App."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Preset & Generated Stories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'English',
                target_age_min INTEGER NOT NULL DEFAULT 2,
                target_age_max INTEGER NOT NULL DEFAULT 9,
                genre TEXT NOT NULL,
                culture_region TEXT NOT NULL,
                parameters_json TEXT,
                audio_file_path TEXT,
                is_generated BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Parent Voice Profiles Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_profiles (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                speaker_name TEXT NOT NULL,
                relationship TEXT NOT NULL,
                profile_status TEXT NOT NULL DEFAULT 'training',
                modulation_profile_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Family Heritage Vault Table (Raw Parent Audio Recordings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recording_vault (
                id TEXT PRIMARY KEY,
                voice_profile_id TEXT NOT NULL,
                story_title TEXT NOT NULL,
                audio_file_path TEXT NOT NULL,
                duration_seconds REAL NOT NULL DEFAULT 0.0,
                modulation_data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voice_profile_id) REFERENCES voice_profiles (id)
            );
        """)

        # 4. Remote Bedroom Speaker Casting Sessions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cast_sessions (
                id TEXT PRIMARY KEY,
                session_name TEXT NOT NULL,
                speaker_protocol TEXT NOT NULL, -- 'Bluetooth', 'AirPlay', 'Chromecast', 'Universal'
                current_story_id TEXT,
                playback_state TEXT NOT NULL DEFAULT 'stopped', -- 'playing', 'paused', 'stopped'
                volume INTEGER NOT NULL DEFAULT 50,
                sleep_timer_minutes INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 5. Parent Account & Subscription Tier Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parent_accounts (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                subscription_tier TEXT NOT NULL DEFAULT 'free', -- 'free', 'premium'
                max_child_profiles INTEGER NOT NULL DEFAULT 2,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 6. Child User Profiles Table (Default Max 2 per free parent profile)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS child_profiles (
                id TEXT PRIMARY KEY,
                parent_user_id TEXT NOT NULL,
                child_name TEXT NOT NULL,
                age INTEGER NOT NULL DEFAULT 5,
                preferred_language TEXT NOT NULL DEFAULT 'Tamil',
                favorite_creature TEXT DEFAULT 'Elephant',
                favorite_genre TEXT DEFAULT 'Bedtime Calm',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_user_id) REFERENCES parent_accounts (id)
            );
        """)

        # 7. Child Listening Analytics & Behavior Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS listening_analytics (
                id TEXT PRIMARY KEY,
                child_id TEXT NOT NULL,
                story_id TEXT NOT NULL,
                play_duration_sec REAL NOT NULL DEFAULT 0.0,
                completion_rate REAL NOT NULL DEFAULT 1.0,
                listened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES child_profiles (id),
                FOREIGN KEY (story_id) REFERENCES stories (id)
            );
        """)

        # Seed default parent account if empty
        cursor.execute("SELECT COUNT(*) FROM parent_accounts;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO parent_accounts (id, email, subscription_tier, max_child_profiles)
                VALUES ('parent_01', 'parent@example.com', 'free', 2);
            """)

        # Seed initial preset stories if table is empty
        cursor.execute("SELECT COUNT(*) FROM stories;")
        if cursor.fetchone()[0] == 0:
            seed_initial_stories(cursor)
            
        # Seed default child profile if empty
        cursor.execute("SELECT COUNT(*) FROM child_profiles;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO child_profiles (id, parent_user_id, child_name, age, preferred_language, favorite_creature, favorite_genre)
                VALUES ('child_aarav', 'parent_01', 'Aarav', 5, 'Tamil', 'Elephant', 'Bedtime Calm');
            """)
            
        conn.commit()

def seed_initial_stories(cursor: sqlite3.Cursor) -> None:
    """Seed initial multilingual stories into catalog."""
    initial_stories = [
        (
            "story_001",
            "Raju the Helpful Elephant",
            "Once upon a time in a lush green village near Madurai, there lived a gentle young elephant named Raju. Raju loved carrying fresh lotus flowers to the village pond...",
            "Tamil",
            2, 6,
            "Bedtime Calm",
            "South Indian",
            json.dumps({"creatures": ["Elephant"], "moral": "Helpfulness"}),
            "/storage/audio_vault/raju_elephant.mp3",
            0
        ),
        (
            "story_002",
            "The Magical Flying Chariot of Hampi",
            "High above the stone temples of Hampi, little Maya discovered a golden chariot with silver wings. As twilight settled, the chariot whispered tales of ancient kings...",
            "English",
            5, 9,
            "Adventure & Mythology",
            "Indian Folklore",
            json.dumps({"creatures": ["Peacock"], "mythology": True}),
            "/storage/audio_vault/flying_chariot.mp3",
            0
        ),
        (
            "story_003",
            "Chintu Squirrel and the Golden Mango",
            "In the bustling gardens of Jaipur, Chintu the squirrel found a glowing golden mango that granted kindness to anyone who shared it...",
            "Hindi",
            3, 7,
            "Bedtime Calm",
            "North Indian",
            json.dumps({"creatures": ["Squirrel"], "moral": "Sharing"}),
            "/storage/audio_vault/golden_mango.mp3",
            0
        )
    ]
    cursor.executemany("""
        INSERT INTO stories (id, title, content, language, target_age_min, target_age_max, genre, culture_region, parameters_json, audio_file_path, is_generated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, initial_stories)
