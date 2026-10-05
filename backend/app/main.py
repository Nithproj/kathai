import json
import sqlite3
import urllib.parse
from wsgiref.simple_server import make_server
from typing import Dict, Any, Tuple

from app.config import SERVER_HOST, SERVER_PORT
from app.database import init_db, get_db_connection
from app.services.llm_service import LLMStoryService
from app.services.voice_service import VoiceService
from app.services.casting_service import RemoteCastingService
from app.services.recommendation_service import RecommendationService
from app.services.profile_service import ChildProfileService

# Initialize SQLite tables on app startup
init_db()

def parse_json_body(environ) -> Dict[str, Any]:
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        if content_length > 0:
            body = environ['wsgi.input'].read(content_length)
            return json.loads(body.decode('utf-8'))
    except Exception:
        pass
    return {}

def json_response(start_response, status_code: int, data: Dict[str, Any]):
    status_map = {200: '200 OK', 201: '201 Created', 400: '400 Bad Request', 404: '404 Not Found', 500: '500 Internal Server Error'}
    status_str = status_map.get(status_code, f'{status_code} OK')
    
    response_body = json.dumps(data).encode('utf-8')
    headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body))),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
        ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    ]
    start_response(status_str, headers)
    return [response_body]

def application(environ, start_response):
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')

    if method == 'OPTIONS':
        return json_response(start_response, 200, {"status": "ok"})

    # 1. Health Endpoint
    if path == '/api/health' and method == 'GET':
        return json_response(start_response, 200, {
            "status": "online",
            "app_name": "Kathai App API Engine",
            "version": "1.6.0"
        })

    # 2. Get Story Catalog
    if path == '/api/stories' and method == 'GET':
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)
        lang_filter = params.get('language', [None])[0]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if lang_filter:
                cursor.execute("SELECT * FROM stories WHERE language = ? ORDER BY created_at DESC;", (lang_filter,))
            else:
                cursor.execute("SELECT * FROM stories ORDER BY created_at DESC;")
            
            rows = cursor.fetchall()
            stories = [dict(row) for row in rows]

        return json_response(start_response, 200, {"stories": stories, "count": len(stories)})

    # 3. Dynamic AI Story Generator
    if path == '/api/stories/generate' and method == 'POST':
        body = parse_json_body(environ)
        genre = body.get('genre', 'Bedtime Calm')
        main_character = body.get('main_character', 'Aarav')
        culture_region = body.get('culture_region', 'South Indian')
        language = body.get('language', 'English')
        is_mythological = body.get('is_mythological', False)
        is_fantasy = body.get('is_fantasy', False)
        creatures = body.get('creatures', ['Friendly Elephant'])
        target_age = body.get('target_age', 5)

        generated = LLMStoryService.generate_story(
            genre=genre,
            main_character=main_character,
            culture_region=culture_region,
            language=language,
            is_mythological=is_mythological,
            is_fantasy=is_fantasy,
            creatures=creatures,
            target_age=target_age
        )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stories (id, title, content, language, target_age_min, target_age_max, genre, culture_region, parameters_json, is_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
            """, (
                generated["id"],
                generated["title"],
                generated["content"],
                generated["language"],
                generated["target_age_min"],
                generated["target_age_max"],
                generated["genre"],
                generated["culture_region"],
                json.dumps(generated["parameters"])
            ))
            conn.commit()

        return json_response(start_response, 201, {"story": generated})

    # 4. Create Child Profile (Default Max 2 Rule)
    if path == '/api/children/profiles' and method == 'POST':
        body = parse_json_body(environ)
        parent_user_id = body.get('parent_user_id', 'parent_01')
        child_name = body.get('child_name', 'Ananya')
        age = int(body.get('age', 4))
        preferred_language = body.get('preferred_language', 'Tamil')
        favorite_creature = body.get('favorite_creature', 'Squirrel')
        favorite_genre = body.get('favorite_genre', 'Bedtime Calm')

        try:
            profile = ChildProfileService.create_child_profile(
                parent_user_id=parent_user_id,
                child_name=child_name,
                age=age,
                preferred_language=preferred_language,
                favorite_creature=favorite_creature,
                favorite_genre=favorite_genre
            )
            return json_response(start_response, 201, {"profile": profile})
        except ValueError as e:
            return json_response(start_response, 400, {"error": str(e)})

    # 5. ONE-TAP SMART QUICK PLAY
    if path == '/api/stories/quick-calm' and method == 'POST':
        body = parse_json_body(environ)
        child_id = body.get('child_id', 'child_aarav')
        result = RecommendationService.get_quick_calming_story(child_id=child_id)
        return json_response(start_response, 200, result)

    # 6. Log Listening Analytics Event
    if path == '/api/analytics/listen' and method == 'POST':
        body = parse_json_body(environ)
        child_id = body.get('child_id', 'child_aarav')
        story_id = body.get('story_id', 'story_001')
        play_duration = float(body.get('play_duration_sec', 180.0))
        completion_rate = float(body.get('completion_rate', 1.0))

        log_res = RecommendationService.log_listening_event(
            child_id=child_id,
            story_id=story_id,
            play_duration_sec=play_duration,
            completion_rate=completion_rate
        )
        return json_response(start_response, 201, log_res)

    # 7. Create Parent Voice Profile
    if path == '/api/voice/profiles' and method == 'POST':
        body = parse_json_body(environ)
        user_id = body.get('user_id', 'parent_default')
        speaker_name = body.get('speaker_name', 'Mom')
        relationship = body.get('relationship', 'Mother')

        profile = VoiceService.create_voice_profile(user_id, speaker_name, relationship)
        return json_response(start_response, 201, {"profile": profile})

    # 8. Record Parent Full Story to Family Vault
    if path == '/api/voice/record' and method == 'POST':
        body = parse_json_body(environ)
        voice_profile_id = body.get('voice_profile_id', 'voice_default')
        story_title = body.get('story_title', 'My Bedtime Story')
        sample_audio = b"SAMPLE_AUDIO_RECORDED_BY_PARENT_WAV_BYTES"

        recording = VoiceService.save_recorded_story(
            voice_profile_id=voice_profile_id,
            story_title=story_title,
            audio_bytes=sample_audio,
            duration_seconds=180.0
        )
        return json_response(start_response, 201, {"recording": recording})

    # 9. Remote Bedroom Speaker Cast Session
    if path == '/api/cast/session' and method == 'GET':
        session = RemoteCastingService.create_or_get_session()
        return json_response(start_response, 200, {"session": session})

    # 10. Remote Bedroom Speaker Control
    if path == '/api/cast/control' and method == 'POST':
        body = parse_json_body(environ)
        session_id = body.get('session_id', 'session_bedroom_01')
        action = body.get('action', 'play')
        story_id = body.get('story_id')
        volume = body.get('volume')
        sleep_timer = body.get('sleep_timer_minutes')

        result = RemoteCastingService.update_playback_control(
            session_id=session_id,
            action=action,
            story_id=story_id,
            volume=volume,
            sleep_timer_minutes=sleep_timer
        )
        return json_response(start_response, 200, {"control": result})

    return json_response(start_response, 404, {"error": "Endpoint not found"})

if __name__ == '__main__':
    print(f"Kathai App Server running on http://{SERVER_HOST}:{SERVER_PORT}")
    httpd = make_server(SERVER_HOST, SERVER_PORT, application)
    httpd.serve_forever()
