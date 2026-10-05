import uuid
import json
from typing import Dict, Any, Optional
from app.database import get_db_connection

class RemoteCastingService:
    """Service managing Parent-Led Remote Bedroom Speaker Casting & Sleep Timer Sessions."""

    @staticmethod
    def create_or_get_session(session_name: str = "Child Bedroom Speaker", speaker_protocol: str = "Bluetooth") -> Dict[str, Any]:
        """Gets or creates a remote casting session for the child's bedroom speaker."""
        session_id = "session_bedroom_01"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cast_sessions WHERE id = ?;", (session_id,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                    INSERT INTO cast_sessions (id, session_name, speaker_protocol, playback_state, volume, sleep_timer_minutes)
                    VALUES (?, ?, ?, 'stopped', 50, 20);
                """, (session_id, session_name, speaker_protocol))
                conn.commit()
                return {
                    "id": session_id,
                    "session_name": session_name,
                    "speaker_protocol": speaker_protocol,
                    "current_story_id": None,
                    "playback_state": "stopped",
                    "volume": 50,
                    "sleep_timer_minutes": 20
                }
            
            return {
                "id": row["id"],
                "session_name": row["session_name"],
                "speaker_protocol": row["speaker_protocol"],
                "current_story_id": row["current_story_id"],
                "playback_state": row["playback_state"],
                "volume": row["volume"],
                "sleep_timer_minutes": row["sleep_timer_minutes"]
            }

    @staticmethod
    def update_playback_control(
        session_id: str,
        action: str, # 'play', 'pause', 'stop', 'volume', 'set_timer'
        story_id: Optional[str] = None,
        volume: Optional[int] = None,
        sleep_timer_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Updates remote playback state, volume, or sleep timer."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cast_sessions WHERE id = ?;", (session_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Cast session not found")

            new_state = row["playback_state"]
            new_story = story_id if story_id else row["current_story_id"]
            new_volume = volume if volume is not None else row["volume"]
            new_timer = sleep_timer_minutes if sleep_timer_minutes is not None else row["sleep_timer_minutes"]

            if action == "play":
                new_state = "playing"
            elif action == "pause":
                new_state = "paused"
            elif action == "stop":
                new_state = "stopped"

            cursor.execute("""
                UPDATE cast_sessions
                SET current_story_id = ?, playback_state = ?, volume = ?, sleep_timer_minutes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (new_story, new_state, new_volume, new_timer, session_id))
            conn.commit()

        return {
            "session_id": session_id,
            "current_story_id": new_story,
            "playback_state": new_state,
            "volume": new_volume,
            "sleep_timer_minutes": new_timer,
            "remote_cast_active": True
        }
