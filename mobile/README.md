# Kathai App — Mobile Client (Flutter)

> **Version:** 1.6.0  
> **Platform Target:** Cross-platform Mobile App (iOS & Android)

---

## 📁 Architecture Overview

```
mobile/
├── pubspec.yaml                  # Project dependencies & assets configuration
├── lib/
│   ├── main.dart                 # Main Material 3 UI entry point (Parent Navigation & Tabs)
│   ├── config/
│   │   └── app_config.dart       # API URLs, Supported Languages, & Tier Limits
│   ├── models/
│   │   └── story.dart            # Story data model & JSON serializers
│   └── services/
│       └── api_service.dart      # REST Client connecting to Python Backend API
```

---

## ⚡ Features Included in Mobile Codebase

1. **🌙 One-Tap Quick Calming Story Banner:** Zero-setup button for exhausted parents at bedtime.
2. **🪄 Interactive Story Co-Creator Wizard:** Input parameters (Main Character name, Genre, Culture/Region, Language, Mythology/Fantasy toggles, Creatures).
3. **🎙️ Parent Recording Studio Teleprompter:** In-app script reader & voice recording suite.
4. **🔊 Bedroom Speaker Remote Player:** Bluetooth, AirPlay, & Chromecast player controls (Play/Pause, Remote Volume slider, Sleep Timer auto-fade).

---

## 🚀 Running the App

```bash
# 1. Install Flutter dependencies
flutter pub get

# 2. Run on connected iOS device / simulator
flutter run -d ios

# 3. Run on connected Android device / emulator
flutter run -d android
```
