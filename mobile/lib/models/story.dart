class Story {
  final String id;
  final String title;
  final String content;
  final String language;
  final int targetAgeMin;
  final int targetAgeMax;
  final String genre;
  final String cultureRegion;
  final String moralConclusion;
  final bool isGenerated;

  Story({
    required this.id,
    required this.title,
    required this.content,
    required this.language,
    required this.targetAgeMin,
    required this.targetAgeMax,
    required this.genre,
    required this.cultureRegion,
    required this.moralConclusion,
    this.isGenerated = false,
  });

  factory Story.fromJson(Map<String, dynamic> json) {
    return Story(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      content: json['content'] ?? '',
      language: json['language'] ?? 'English',
      targetAgeMin: json['target_age_min'] ?? 2,
      targetAgeMax: json['target_age_max'] ?? 9,
      genre: json['genre'] ?? 'Bedtime Calm',
      cultureRegion: json['culture_region'] ?? 'South Indian',
      moralConclusion: json['moral_conclusion'] ?? '',
      isGenerated: json['is_generated'] == 1 || json['is_generated'] == true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'language': language,
      'target_age_min': targetAgeMin,
      'target_age_max': targetAgeMax,
      'genre': genre,
      'culture_region': cultureRegion,
      'moral_conclusion': moralConclusion,
      'is_generated': isGenerated,
    };
  }
}
