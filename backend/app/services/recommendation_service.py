import uuid
import json
from typing import Dict, Any, Optional
from app.database import get_db_connection
from app.services.llm_service import LLMStoryService

class RecommendationService:
    """Service to handle One-Tap Smart Play & Child Listening Pattern Analysis."""

    @staticmethod
    def get_quick_calming_story(child_id: str = "child_aarav") -> Dict[str, Any]:
        """
        Analyzes child listening patterns and returns either:
        1. The child's most listened favorite calm story (Replay), or
        2. A freshly auto-generated calming bedtime story customized to learned preferences.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Fetch child profile preferences
            cursor.execute("SELECT * FROM child_profiles WHERE id = ?;", (child_id,))
            child = cursor.fetchone()
            if not child:
                # Fallback default profile if not found
                child_name = "Aarav"
                language = "Tamil"
                creature = "Elephant"
                age = 5
            else:
                child_name = child["child_name"]
                language = child["preferred_language"]
                creature = child["favorite_creature"]
                age = child["age"]

            # 2. Check for most completed favorite stories (Completion rate >= 0.8)
            cursor.execute("""
                SELECT s.*, COUNT(la.id) as play_count, AVG(la.completion_rate) as avg_completion
                FROM listening_analytics la
                JOIN stories s ON la.story_id = s.id
                WHERE la.child_id = ? AND la.completion_rate >= 0.8
                GROUP BY s.id
                ORDER BY play_count DESC, avg_completion DESC
                LIMIT 1;
            """, (child_id,))
            favorite_row = cursor.fetchone()

            # If child has a clear top favorite, return it as a One-Tap Replay candidate
            if favorite_row and favorite_row["play_count"] >= 2:
                fav_story = dict(favorite_row)
                return {
                    "mode": "favorite_replay",
                    "reason": f"Most-listened bedtime favorite for {child_name} (Played {fav_story['play_count']} times)",
                    "story": {
                        "id": fav_story["id"],
                        "title": fav_story["title"],
                        "content": fav_story["content"],
                        "language": fav_story["language"],
                        "genre": fav_story["genre"],
                        "culture_region": fav_story["culture_region"]
                    }
                }

            # 3. Otherwise, auto-generate a fresh personalized bedtime calm story
            auto_generated = LLMStoryService.generate_story(
                genre="Bedtime Calm",
                main_character=child_name,
                culture_region="South Indian" if language == "Tamil" else "Indian Folklore",
                language=language,
                is_mythological=False,
                is_fantasy=True,
                creatures=[creature],
                target_age=age
            )

            # Insert auto-generated story into DB
            cursor.execute("""
                INSERT INTO stories (id, title, content, language, target_age_min, target_age_max, genre, culture_region, parameters_json, is_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
            """, (
                auto_generated["id"],
                auto_generated["title"],
                auto_generated["content"],
                auto_generated["language"],
                auto_generated["target_age_min"],
                auto_generated["target_age_max"],
                auto_generated["genre"],
                auto_generated["culture_region"],
                json.dumps(auto_generated["parameters"])
            ))
            conn.commit()

            return {
                "mode": "smart_auto_generate",
                "reason": f"Auto-generated calming story for {child_name} based on favorite {creature} & bedtime pattern",
                "story": auto_generated
            }

    @staticmethod
    def log_listening_event(child_id: str, story_id: str, play_duration_sec: float, completion_rate: float) -> Dict[str, Any]:
        """Logs a child listening event to train pattern analysis."""
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO listening_analytics (id, child_id, story_id, play_duration_sec, completion_rate)
                VALUES (?, ?, ?, ?, ?);
            """, (event_id, child_id, story_id, play_duration_sec, completion_rate))
            conn.commit()

        return {"event_id": event_id, "child_id": child_id, "story_id": story_id, "status": "logged"}
