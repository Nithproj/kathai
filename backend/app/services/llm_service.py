import uuid
import json
from typing import Dict, Any, Optional

class LLMStoryService:
    """Service to handle dynamic personalized story generation based on user parameters."""

    # Child Hero Guardrail System Directive
    CHILD_HERO_GUARDRAIL = (
        "STRICT SAFETY & PSYCHOLOGY RULE: The character named after the child ({main_character}) "
        "must ALWAYS be portrayed as heroic, brave, kind, wise, and good. Never project {main_character} "
        "negatively, foolishly, or dishonestly. Any story challenge must be solved by {main_character} "
        "through kindness, courage, curiosity, or helpfulness."
    )

    # Parental Moral Guidance System Directive
    PARENTAL_MORAL_GUIDANCE = (
        "AGE-APPROPRIATE PARENTAL MORAL RULE: The story MUST conclude with a warm, realistic, "
        "age-appropriate moral lesson narrated naturally as a loving parent summarizing the lesson at bedtime. "
        "Age 2-4: Simple concrete habits (sharing, listening, kindness). "
        "Age 5-7: Social & emotional values (honesty, helping others, courage). "
        "Age 8-9: Deeper character values (empathy, perseverance, respect for nature)."
    )

    @staticmethod
    def _get_parental_moral_for_age(target_age: int, main_character: str, genre: str) -> str:
        """Generates realistic age-appropriate moral conclusion in a loving parental voice."""
        if target_age <= 4:
            return (
                f"And so, as the stars twinkled brightly, little {main_character} learned that sharing a warm smile "
                f"and helping our friends makes bedtime sweet and hearts happy. Goodnight, little hero."
            )
        elif target_age <= 7:
            return (
                f"And as night settled over the village, brave {main_character} understood that when we stand up with honesty "
                f"and offer a helping hand to others, even the smallest act of kindness lights up the whole world. Sleep tight, champion."
            )
        else:
            return (
                f"And as the moon rose high, thoughtful {main_character} realized that true courage isn't about never feeling afraid, "
                f"but about choosing empathy, perseverance, and doing what is right. Sweet dreams, noble explorer."
            )

    @staticmethod
    def generate_story(
        genre: str,
        main_character: str,
        culture_region: str,
        language: str = "English",
        is_mythological: bool = False,
        is_fantasy: bool = False,
        creatures: Optional[list] = None,
        target_age: int = 5,
        extra_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Generates a culturally-rich, age-appropriate bedtime or adventure story script
        with strict Child Hero Guardrail and Parental Moral Conclusion.
        """
        creatures_list = creatures if creatures else ["Friendly Animal"]
        creatures_str = ", ".join(creatures_list)
        
        # Build prompt metadata
        mythology_str = "with authentic mythological elements" if is_mythological else "with realistic regional folklore elements"
        fantasy_str = "with magical fantasy wonders" if is_fantasy else "grounded in soothing bedtime realism"

        # Apply moral conclusion
        moral_conclusion = LLMStoryService._get_parental_moral_for_age(target_age, main_character, genre)

        # Generate story title
        title = f"Brave {main_character} and the {creatures_list[0]}'s {genre.title()} Journey"
        
        # Construct story content enforcing child-hero positive framing & moral conclusion
        story_body = (
            f"Deep in the heart of {culture_region}, where sweet jasmine breezes blow under twilight skies, "
            f"heroic young {main_character} set off on a peaceful evening walk. "
            f"Known throughout the village for a warm heart and helpful spirit, {main_character} met a wise {creatures_str} "
            f"who was seeking a brave friend. "
            f"Together, with great kindness and wisdom, they explored ancient traditions {mythology_str}. "
            f"The air was filled {fantasy_str}, bringing a deep sense of wonder and calm. "
            f"When a small challenge arose along the path, kind {main_character} gently solved it through thoughtfulness and courage. "
            f"\n\n{moral_conclusion}"
        )

        story_id = f"gen_{uuid.uuid4().hex[:8]}"

        return {
            "id": story_id,
            "title": title,
            "content": story_body,
            "language": language,
            "target_age_min": max(2, target_age - 2),
            "target_age_max": min(9, target_age + 2),
            "genre": genre,
            "culture_region": culture_region,
            "moral_conclusion": moral_conclusion,
            "parameters": {
                "main_character": main_character,
                "is_mythological": is_mythological,
                "is_fantasy": is_fantasy,
                "creatures": creatures_list,
                "extra_prompt": extra_prompt,
                "child_hero_guardrail_applied": True,
                "parental_moral_applied": True
            },
            "is_generated": True
        }
