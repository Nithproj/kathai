import unittest
import json
import sqlite3
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DB_PATH
from app.database import init_db, get_db_connection
from app.services.llm_service import LLMStoryService
from app.services.voice_service import VoiceService
from app.services.casting_service import RemoteCastingService
from app.services.recommendation_service import RecommendationService
from app.services.profile_service import ChildProfileService

class TestKathaiBackend(unittest.TestCase):

    def setUp(self):
        """Set up fresh database for testing."""
        if DB_PATH.exists():
            try:
                os.remove(DB_PATH)
            except Exception:
                pass
        init_db()

    def test_database_seeding(self):
        """Test that preset stories, parent account, and child profile are seeded into DB."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stories;")
            count = cursor.fetchone()[0]
            self.assertGreaterEqual(count, 3)

            cursor.execute("SELECT COUNT(*) FROM child_profiles;")
            child_count = cursor.fetchone()[0]
            self.assertGreaterEqual(child_count, 1)

    def test_child_profile_tier_limit(self):
        """Test that default free parent account allows max 2 child profiles, blocking 3rd."""
        # 1. Create second profile for parent_01 (1st was seeded as child_aarav)
        p2 = ChildProfileService.create_child_profile("parent_01", "Ananya", 3, "Tamil")
        self.assertEqual(p2["profiles_used"], 2)
        self.assertEqual(p2["max_allowed"], 2)

        # 2. Attempting to create 3rd profile should raise ValueError requiring tier upgrade
        with self.assertRaises(ValueError) as ctx:
            ChildProfileService.create_child_profile("parent_01", "Kiran", 6, "Hindi")
        self.assertIn("limit reached", str(ctx.exception).lower())

    def test_llm_story_generator(self):
        """Test dynamic story script generation based on user parameters."""
        story = LLMStoryService.generate_story(
            genre="Adventure",
            main_character="Kavya",
            culture_region="South Indian",
            language="Tamil",
            is_mythological=True,
            is_fantasy=True,
            creatures=["Magical Peacock"],
            target_age=6
        )

        self.assertIn("Kavya", story["title"])
        self.assertIn("South Indian", story["content"])
        self.assertEqual(story["genre"], "Adventure")
        self.assertTrue(story["is_generated"])

    def test_child_hero_guardrail(self):
        """Test that child-named characters are strictly portrayed positively and heroically."""
        story = LLMStoryService.generate_story(
            genre="Bedtime Calm",
            main_character="Aarav",
            culture_region="South Indian",
            language="Tamil"
        )

        self.assertTrue(story["parameters"]["child_hero_guardrail_applied"])
        self.assertIn("heroic", story["content"].lower())
        self.assertIn("kindness", story["content"].lower())
        self.assertNotIn("foolish", story["content"].lower())
        self.assertNotIn("greedy", story["content"].lower())

    def test_parental_moral_engine(self):
        """Test that stories conclude with warm, realistic age-scaled parental morals."""
        story_toddler = LLMStoryService.generate_story(genre="Bedtime Calm", main_character="Ananya", culture_region="South Indian", target_age=3)
        self.assertTrue(story_toddler["parameters"]["parental_moral_applied"])
        self.assertIn("sharing", story_toddler["moral_conclusion"].lower())

    def test_quick_calm_one_tap_recommendation(self):
        """Test One-Tap Quick Play feature for exhausted parents."""
        RecommendationService.log_listening_event("child_aarav", "story_001", 180.0, 1.0)
        RecommendationService.log_listening_event("child_aarav", "story_001", 180.0, 0.95)

        result = RecommendationService.get_quick_calming_story("child_aarav")
        self.assertIn("mode", result)
        self.assertIn("story", result)
        self.assertEqual(result["mode"], "favorite_replay")
        self.assertEqual(result["story"]["id"], "story_001")

    def test_parent_voice_profile_and_vault(self):
        """Test creating voice profile and saving parent story recording."""
        profile = VoiceService.create_voice_profile("user_01", "Amma", "Mother")
        self.assertEqual(profile["speaker_name"], "Amma")

        recording = VoiceService.save_recorded_story(
            voice_profile_id=profile["id"],
            story_title="Grandma's Lotus Story",
            audio_bytes=b"TEST_WAV_BYTES",
            duration_seconds=120.0
        )
        self.assertEqual(recording["story_title"], "Grandma's Lotus Story")
        self.assertEqual(recording["duration_seconds"], 120.0)

    def test_remote_casting_service(self):
        """Test remote speaker session creation and volume/sleep timer controls."""
        session = RemoteCastingService.create_or_get_session("Kid Room Echo", "Bluetooth")
        self.assertIn(session["speaker_protocol"], ["Bluetooth", "Universal"])

        updated = RemoteCastingService.update_playback_control(
            session_id=session["id"],
            action="play",
            volume=70,
            sleep_timer_minutes=30
        )
        self.assertEqual(updated["playback_state"], "playing")
        self.assertEqual(updated["volume"], 70)
        self.assertEqual(updated["sleep_timer_minutes"], 30)

if __name__ == "__main__":
    unittest.main()
