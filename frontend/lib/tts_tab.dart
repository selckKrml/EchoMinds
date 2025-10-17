import 'dart:typed_data';
import 'config.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'database_helper.dart';
import 'package:audioplayers/audioplayers.dart';

class TextToSpeechTab extends StatefulWidget {
  const TextToSpeechTab({super.key});

  @override
  State<TextToSpeechTab> createState() => _TextToSpeechTabState();
}

class _TextToSpeechTabState extends State<TextToSpeechTab> {
  List<Recording> _recordings = [];
  bool _isLoading = true;
  String _statusText = '';
  final TextEditingController _textController = TextEditingController();
  final AudioPlayer _audioPlayer = AudioPlayer();

  // Sunucu ve ses ayarları
  final String _serverIp = serverIp; // KENDİ IP ADRESİNİ YAZ
  String _selectedVoiceId = "pNInz6obpgDQGcFmaJgB"; // Varsayılan: Adam
  String _targetLang = 'tr'; // Varsayılan: Türkçe

  @override
  void initState() {
    super.initState();
    _refreshRecordings();
  }

  Future<void> _refreshRecordings() async {
    setState(() => _isLoading = true);
    final data = await DatabaseHelper.instance.readAllRecordings();
    setState(() {
      _recordings = data;
      _isLoading = false;
    });
  }

  Future<void> _deleteRecording(int id) async {
    await DatabaseHelper.instance.delete(id);
    _refreshRecordings();
  }

  Future<void> _textToSpeech() async {
    final text = _textController.text;
    if (text.isEmpty) {
      setState(() => _statusText = 'Lütfen seslendirilecek bir metin seçin veya yazın.');
      return;
    }

    setState(() => _statusText = '🔊 Ses oluşturuluyor...');
    try {
      var uri = Uri.parse('http://$_serverIp:5000/tts');
      var response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'text': text,
          'voice_id': _selectedVoiceId,
          'target_lang': _targetLang,
        }),
      );

      if (response.statusCode == 200) {
        final Uint8List audioBytes = response.bodyBytes;
        await _audioPlayer.play(BytesSource(audioBytes));
        setState(() => _statusText = '✅ Seslendirme tamamlandı!');
      } else {
        setState(() => _statusText = 'Sunucu Hatası: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _statusText = 'Hata: Sunucuya bağlanılamadı.');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: TextField(
            controller: _textController,
            decoration: const InputDecoration(
              labelText: 'Seslendirilecek Metin',
              border: OutlineInputBorder(),
            ),
            maxLines: 3,
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              // SES SEÇİMİ VE DİL SEÇİMİ EKLENECEK (ŞİMDİLİK BASİT)
              ElevatedButton.icon(
                onPressed: _textToSpeech,
                icon: const Icon(Icons.volume_up),
                label: const Text('Konuş'),
              ),
            ],
          ),
        ),
        if (_statusText.isNotEmpty) Padding(
          padding: const EdgeInsets.all(8.0),
          child: Text(_statusText),
        ),
        const Divider(),
        const Text('Kaydedilmiş Metinler', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        Expanded(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: _recordings.length,
                  itemBuilder: (context, index) {
                    final recording = _recordings[index];
                    return ListTile(
                      title: Text(recording.text, maxLines: 2, overflow: TextOverflow.ellipsis),
                      subtitle: Text(recording.createdAt),
                      onTap: () {
                        _textController.text = recording.text;
                      },
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () => _deleteRecording(recording.id!),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}