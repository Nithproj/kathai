class AppConfig {
  static const String appName = 'Kathai App';
  static const String appVersion = '1.6.0';
  static const String apiBaseUrl = 'http://localhost:8000/api';

  // Supported Languages
  static const List<String> supportedLanguages = [
    'Tamil',
    'Hindi',
    'English',
    'Telugu',
    'Malayalam',
    'Kannada',
    'Marathi',
    'Bengali',
    'Spanish',
    'French',
  ];

  // Max Child Profiles for Free Tier
  static const int freeTierMaxChildProfiles = 2;
}
