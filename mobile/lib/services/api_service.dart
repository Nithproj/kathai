import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/story.dart';

class ApiService {
  final String baseUrl;

  ApiService({this.baseUrl = AppConfig.apiBaseUrl});

  /// Fetch story catalog
  Future<List<Story>> fetchStories({String? language}) async {
    final Uri url = Uri.parse('$baseUrl/stories${language != null ? "?language=$language" : ""}');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final List list = data['stories'] ?? [];
      return list.map((item) => Story.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load stories catalog');
    }
  }

  /// One-Tap Quick Calming Story (Exhausted Parent Mode)
  Future<Map<String, dynamic>> fetchQuickCalmStory(String childId) async {
    final Uri url = Uri.parse('$baseUrl/stories/quick-calm');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'child_id': childId}),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to fetch quick calm story');
    }
  }

  /// Dynamic AI Story Generator
  Future<Story> generateStory({
    required String mainCharacter,
    required String genre,
    required String cultureRegion,
    required String language,
    bool isMythological = false,
    bool isFantasy = false,
    List<String>? creatures,
    int targetAge = 5,
  }) async {
    final Uri url = Uri.parse('$baseUrl/stories/generate');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'main_character': mainCharacter,
        'genre': genre,
        'culture_region': cultureRegion,
        'language': language,
        'is_mythological': isMythological,
        'is_fantasy': isFantasy,
        'creatures': creatures ?? ['Friendly Elephant'],
        'target_age': targetAge,
      }),
    );

    if (response.statusCode == 201) {
      final data = json.decode(response.body);
      return Story.fromJson(data['story']);
    } else {
      throw Exception('Failed to generate story');
    }
  }

  /// Remote Bedroom Speaker Control
  Future<Map<String, dynamic>> updateCastControl({
    required String sessionId,
    required String action,
    String? storyId,
    int? volume,
    int? sleepTimerMinutes,
  }) async {
    final Uri url = Uri.parse('$baseUrl/cast/control');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'session_id': sessionId,
        'action': action,
        'story_id': storyId,
        'volume': volume,
        'sleep_timer_minutes': sleepTimerMinutes,
      }),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to update remote speaker control');
    }
  }
}
