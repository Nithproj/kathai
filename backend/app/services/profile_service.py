import uuid
import json
from typing import Dict, Any, List, Optional
from app.database import get_db_connection

class ChildProfileService:
    """Service handling child profile management and tier limits."""

    @staticmethod
    def create_child_profile(
        parent_user_id: str,
        child_name: str,
        age: int,
        preferred_language: str = "Tamil",
        favorite_creature: str = "Elephant",
        favorite_genre: str = "Bedtime Calm"
    ) -> Dict[str, Any]:
        """
        Creates a child profile enforcing the Max 2 Profiles limit for Free accounts.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Fetch parent account tier and profile limit
            cursor.execute("SELECT subscription_tier, max_child_profiles FROM parent_accounts WHERE id = ?;", (parent_user_id,))
            parent = cursor.fetchone()
            if not parent:
                # Default fallback if parent account record doesn't exist yet
                tier = 'free'
                max_allowed = 2
            else:
                tier = parent["subscription_tier"]
                max_allowed = parent["max_child_profiles"] if tier == 'free' else 999

            # 2. Count existing child profiles for this parent
            cursor.execute("SELECT COUNT(*) FROM child_profiles WHERE parent_user_id = ?;", (parent_user_id,))
            existing_count = cursor.fetchone()[0]

            if existing_count >= max_allowed:
                raise ValueError(
                    f"Child profile limit reached ({existing_count}/{max_allowed} on {tier.upper()} tier). "
                    "Please upgrade to Premium for unlimited child profiles."
                )

            # 3. Create new child profile
            child_id = f"child_{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO child_profiles (id, parent_user_id, child_name, age, preferred_language, favorite_creature, favorite_genre)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (child_id, parent_user_id, child_name, age, preferred_language, favorite_creature, favorite_genre))
            conn.commit()

            return {
                "id": child_id,
                "parent_user_id": parent_user_id,
                "child_name": child_name,
                "age": age,
                "preferred_language": preferred_language,
                "favorite_creature": favorite_creature,
                "favorite_genre": favorite_genre,
                "profiles_used": existing_count + 1,
                "max_allowed": max_allowed
            }
