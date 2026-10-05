import 'package:flutter/material.dart';
import 'config/app_config.dart';
import 'models/story.dart';
import 'services/api_service.dart';

void main() {
  runApp(const KathaiApp());
}

class KathaiApp extends StatelessWidget {
  const KathaiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF4F46E5),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0F172A),
      ),
      home: const ParentHomeScreen(),
    );
  }
}

class ParentHomeScreen extends StatefulWidget {
  const ParentHomeScreen({super.key});

  @override
  State<ParentHomeScreen> createState() => _ParentHomeScreenState();
}

class _ParentHomeScreenState extends State<ParentHomeScreen> {
  int _selectedIndex = 0;
  final ApiService _apiService = ApiService();
  
  // Controllers
  final TextEditingController _charController = TextEditingController(text: 'Aarav');
  String _selectedGenre = 'Bedtime Calm';
  String _selectedRegion = 'South Indian (Tamil)';
  String _selectedLanguage = 'Tamil';
  bool _includeMythology = true;
  bool _includeFantasy = true;
  String _selectedCreature = 'Friendly Elephant (Raju)';
  
  Story? _generatedStory;
  bool _isGenerating = false;
  
  // Remote Speaker Player State
  int _volume = 50;
  bool _isPlaying = false;
  String _activeStoryTitle = "Raju the Helpful Elephant";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E1B4B),
        title: Row(
          children: [
            const Text('📖 ', style: TextStyle(fontSize: 20)),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Kathai App', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                Text('Parent Studio & Remote Cast (v${AppConfig.appVersion})', style: const TextStyle(fontSize: 10, color: Colors.white70)),
              ],
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 12),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.emerald.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.emerald),
            ),
            child: const Row(
              children: [
                Icon(Icons.bluetooth_connected, size: 14, color: Colors.emerald),
                SizedBox(width: 4),
                Text("Aarav's Room", style: TextStyle(fontSize: 11, color: Colors.emerald, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // ONE-TAP QUICK CALM BANNER (Exhausted Parent Mode)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF312E81), Color(0xFF581C87)],
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('🌙 Quick Calming Bedtime Story', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.white)),
                      Text('Zero setup. Replays Aarav\'s favorite or auto-generates calm.', style: TextStyle(fontSize: 10, color: Colors.white70)),
                    ],
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: _triggerQuickCalm,
                  icon: const Icon(Icons.bolt, size: 14, color: Colors.white),
                  label: const Text('One-Tap Play', style: TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.emerald,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                ),
              ],
            ),
          ),

          // TAB BODY VIEWS
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: [
                _buildStoryCreatorTab(),
                _buildRecordingStudioTab(),
                _buildRemotePlayerTab(),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (idx) => setState(() => _selectedIndex = idx),
        backgroundColor: const Color(0xFF0F172A),
        selectedItemColor: const Color(0xFF818CF8),
        unselectedItemColor: Colors.white54,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.auto_awesome), label: 'Story Creator'),
          BottomNavigationBarItem(icon: Icon(Icons.mic), label: 'Voice Studio'),
          BottomNavigationBarItem(icon: Icon(Icons.speaker), label: 'Room Player'),
        ],
      ),
    );
  }

  // TAB 1: STORY CO-CREATOR WIZARD
  Widget _buildStoryCreatorTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Step 1: Co-Create Bedtime Story', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white70)),
          const SizedBox(height: 12),

          // Main Character
          TextField(
            controller: _charController,
            decoration: const InputDecoration(
              labelText: 'Child / Main Character Name',
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
          const SizedBox(height: 12),

          // Genre & Region
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedGenre,
                  decoration: const InputDecoration(labelText: 'Genre', isDense: true, border: OutlineInputBorder()),
                  items: ['Bedtime Calm', 'Moral & Values', 'Adventure', 'Mystery']
                      .map((g) => DropdownMenuItem(value: g, child: Text(g, style: const TextStyle(fontSize: 12)))).toList(),
                  onChanged: (val) => setState(() => _selectedGenre = val!),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedLanguage,
                  decoration: const InputDecoration(labelText: 'Language', isDense: true, border: OutlineInputBorder()),
                  items: AppConfig.supportedLanguages
                      .map((l) => DropdownMenuItem(value: l, child: Text(l, style: const TextStyle(fontSize: 12)))).toList(),
                  onChanged: (val) => setState(() => _selectedLanguage = val!),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Toggles
          Row(
            children: [
              Expanded(
                child: CheckboxListTile(
                  title: const Text('Mythology', style: TextStyle(fontSize: 11)),
                  value: _includeMythology,
                  onChanged: (val) => setState(() => _includeMythology = val!),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                ),
              ),
              Expanded(
                child: CheckboxListTile(
                  title: const Text('Fantasy', style: TextStyle(fontSize: 11)),
                  value: _includeFantasy,
                  onChanged: (val) => setState(() => _includeFantasy = val!),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton.icon(
              onPressed: _isGenerating ? null : _generateStory,
              icon: const Icon(Icons.auto_awesome),
              label: Text(_isGenerating ? 'Generating...' : '🪄 Generate & Cast to Room'),
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF4F46E5)),
            ),
          ),

          if (_generatedStory != null) ...[
            const SizedBox(height: 16),
            Card(
              color: const Color(0xFF1E293B),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(_generatedStory!.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.emeraldAccent)),
                    const SizedBox(height: 6),
                    Text(_generatedStory!.content, style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
                    const SizedBox(height: 10),
                    ElevatedButton(
                      onPressed: () => setState(() => _selectedIndex = 2),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.emerald),
                      child: const Text('▶️ Stream to Bedroom Speaker', style: TextStyle(color: Colors.white, fontSize: 12)),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // TAB 2: IN-APP RECORDING STUDIO
  Widget _buildRecordingStudioTab() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Parent Recording Teleprompter', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(color: const Color(0xFF1E293B), borderRadius: BorderRadius.circular(12)),
            child: const Text(
              '"Once upon a time, high in the hills of Madurai, young Aarav met Raju the gentle elephant under a giant banyan tree..."',
              style: TextStyle(fontSize: 14, height: 1.4),
            ),
          ),
          const SizedBox(height: 24),
          Center(
            child: ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.fiber_manual_record, color: Colors.red),
              label: const Text('Record Parent Story'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red.withOpacity(0.2)),
            ),
          ),
        ],
      ),
    );
  }

  // TAB 3: REMOTE ROOM PLAYER
  Widget _buildRemotePlayerTab() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Card(
            color: const Color(0xFF1E1B4B),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text('CONNECTED: Aarav\'s Bedroom Speaker (Bluetooth)', style: TextStyle(fontSize: 10, color: Colors.emerald)),
                  const SizedBox(height: 8),
                  Text(_activeStoryTitle, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const Text('Narrated in Amma\'s Voice', style: TextStyle(fontSize: 12, color: Colors.white70)),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      IconButton(onPressed: () {}, icon: const Icon(Icons.replay_10)),
                      IconButton(
                        iconSize: 48,
                        icon: Icon(_isPlaying ? Icons.pause_circle_filled : Icons.play_circle_fill, color: Colors.emerald),
                        onPressed: () => setState(() => _isPlaying = !_isPlaying),
                      ),
                      IconButton(onPressed: () {}, icon: const Icon(Icons.forward_10)),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              const Icon(Icons.volume_down),
              Expanded(
                child: Slider(
                  value: _volume.toDouble(),
                  min: 0,
                  max: 100,
                  activeColor: Colors.emerald,
                  onChanged: (val) => setState(() => _volume = val.round()),
                ),
              ),
              Text('$_volume%'),
            ],
          ),
        ],
      ),
    );
  }

  void _triggerQuickCalm() {
    setState(() {
      _activeStoryTitle = "Raju the Helpful Elephant (Favorite Replay)";
      _isPlaying = true;
      _selectedIndex = 2;
    });
  }

  void _generateStory() async {
    setState(() => _isGenerating = true);
    try {
      final story = await _apiService.generateStory(
        mainCharacter: _charController.text,
        genre: _selectedGenre,
        cultureRegion: _selectedRegion,
        language: _selectedLanguage,
        isMythological: _includeMythology,
        isFantasy: _includeFantasy,
      );
      setState(() {
        _generatedStory = story;
        _activeStoryTitle = story.title;
        _isGenerating = false;
      });
    } catch (e) {
      setState(() => _isGenerating = false);
    }
  }
}
