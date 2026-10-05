import os
import uuid
import json
from typing import Dict, Any, List, Optional
from app.config import AUDIO_VAULT_DIR, VOICE_PROFILES_DIR
from app.database import get_db_connection

class VoiceService:
    """Service to handle parent voice cloning, recording studio ingestion, and family vault storage."""

    @staticmethod
    def create_voice_profile(user_id: str, speaker_name: str, relationship: str) -> Dict[str, Any]:
        """Creates a new parent or grandparent voice profile."""
        profile_id = f"voice_{uuid.uuid4().hex[:8]}"
        initial_modulation = {
            "pitch_range": "medium",
            "narrative_pace": "gentle",
            "modulation_samples_count": 0,
            "character_voice_accents": []
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO voice_profiles (id, user_id, speaker_name, relationship, profile_status, modulation_profile_json)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (profile_id, user_id, speaker_name, relationship, 'ready', json.dumps(initial_modulation)))
            conn.commit()

        return {
            "id": profile_id,
            "user_id": user_id,
            "speaker_name": speaker_name,
            "relationship": relationship,
            "profile_status": "ready",
            "modulation_profile": initial_modulation
        }

    @staticmethod
    def save_recorded_story(
        voice_profile_id: str,
        story_title: str,
        audio_bytes: bytes,
        duration_seconds: float = 180.0
    ) -> Dict[str, Any]:
        """
        Saves a full parent story recording into the Family Heritage Vault
        and updates the AI voice modulation profile.
        """
        recording_id = f"rec_{uuid.uuid4().hex[:8]}"
        filename = f"{recording_id}.wav"
        file_path = str(AUDIO_VAULT_DIR / filename)

        # Write audio bytes to file
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Extract modulation metrics (mock metrics calculation for audio analysis)
        modulation_data = {
            "duration": duration_seconds,
            "pitch_variance": 0.85,
            "expressiveness_score": 9.2,
            "pause_cadence": "bedtime_calm",
            "sample_rate_hz": 44100
        }

        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 1. Insert into recording_vault
            cursor.execute("""
                INSERT INTO recording_vault (id, voice_profile_id, story_title, audio_file_path, duration_seconds, modulation_data_json)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (recording_id, voice_profile_id, story_title, file_path, duration_seconds, json.dumps(modulation_data)))

            # 2. Update voice profile sample count and modulation profile
            cursor.execute("SELECT modulation_profile_json FROM voice_profiles WHERE id = ?;", (voice_profile_id,))
            row = cursor.fetchone()
            if row:
                current_profile = json.loads(row[0]) if row[0] else {}
                current_profile["modulation_samples_count"] = current_profile.get("modulation_samples_count", 0) + 1
                current_profile["last_recording_id"] = recording_id
                
                cursor.execute("""
                    UPDATE voice_profiles
                    SET modulation_profile_json = ?, profile_status = 'trained'
                    WHERE id = ?;
                """, (json.dumps(current_profile), voice_profile_id))

            conn.commit()

        return {
            "id": recording_id,
            "voice_profile_id": voice_profile_id,
            "story_title": story_title,
            "audio_file_path": file_path,
            "duration_seconds": duration_seconds,
            "modulation_data": modulation_data
        }

    @staticmethod
    def synthesize_story_audio(story_id: str, voice_profile_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesizes audio for a story script using either the trained Parent Voice profile
        or standard studio narrator.
        """
        synthesis_id = f"synth_{uuid.uuid4().hex[:8]}"
        output_path = str(AUDIO_VAULT_DIR / f"{synthesis_id}.mp3")

        voice_mode = "Parent Voice (Cloned)" if voice_profile_id else "Studio Narrator"

        # Create a placeholder audio file if synthesizing
        with open(output_path, "wb") as f:
            f.write(b"AUDIO_HEADER_KATHAI_APP_PLACEHOLDER")

        return {
            "synthesis_id": synthesis_id,
            "story_id": story_id,
            "voice_profile_id": voice_profile_id,
            "voice_mode": voice_mode,
            "audio_url": f"/api/audio/{synthesis_id}",
            "status": "ready"
        }
