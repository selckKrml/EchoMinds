// (importlar aynı kalacak)
import 'package:flutter/material.dart';
import 'config.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'database_helper.dart'; // Veritabanını ekledik

// (class tanımı aynı kalacak)
class SpeechToTextTab extends StatefulWidget {
  const SpeechToTextTab({super.key});

  @override
  State<SpeechToTextTab> createState() => _SpeechToTextTabState();
}

class _SpeechToTextTabState extends State<SpeechToTextTab> {
  // (değişkenler aynı kalacak)
  final FlutterSoundRecorder _recorder = FlutterSoundRecorder();
  bool _isRecorderInitialized = false;
  bool _isRecording = false;
  String _statusText = 'Kayda başlamak için butona basın.';
  String _originalText = '';
  String _translatedText = '';
  String _targetLang = 'en';
  final String _audioFilePath = 'stt_audio.aac';
  final String _serverIp = serverIp; // KENDİ IP ADRESİNİ YAZ

  // (initState ve initializeRecorder aynı kalacak)
  @override
  void initState() {
    super.initState();
    _initializeRecorder();
  }

  Future<void> _initializeRecorder() async {
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      throw RecordingPermissionException('Mikrofon izni verilmedi.');
    }
    await _recorder.openRecorder();
    setState(() {
      _isRecorderInitialized = true;
    });
  }
  
  // (toggleRecording aynı kalacak)
  Future<void> _toggleRecording() async {
    if (!_isRecorderInitialized) return;

    if (_isRecording) {
      await _recorder.stopRecorder();
      setState(() {
        _statusText = '✅ Kayıt tamamlandı. Sunucuya gönderiliyor...';
        _isRecording = false;
      });
      _uploadAndTranscribe();
    } else {
      setState(() {
        _statusText = '🔴 Kayıt yapılıyor...';
        _isRecording = true;
        _originalText = '';
        _translatedText = '';
      });
      await _recorder.startRecorder(toFile: _audioFilePath, codec: Codec.aacADTS);
    }
  }

  Future<void> _uploadAndTranscribe() async {
    // (Bu fonksiyonun başına setState kısmı aynı kalacak)
    setState(() {
       _statusText = '✍️ Ses metne çevriliyor... Lütfen bekleyin.';
    });

    try {
      var uri = Uri.parse('http://$_serverIp:5000/stt');
      var request = http.MultipartRequest('POST', uri)
        ..fields['target_lang'] = _targetLang
        ..files.add(await http.MultipartFile.fromPath('audio', _audioFilePath));

      var response = await request.send();

      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        final decodedBody = json.decode(responseBody);
        
        // --- YENİ EKLENEN KISIM ---
        await DatabaseHelper.instance.create(decodedBody['original_text']);
        // --- YENİ KISIM BİTTİ ---

        setState(() {
          _originalText = decodedBody['original_text'];
          _translatedText = decodedBody['translated_text'];
          _statusText = 'Çeviri başarıyla tamamlandı ve kaydedildi!';
        });
      } else {
        // (hata yönetimi aynı kalacak)
        final errorBody = await response.stream.bytesToString();
        setState(() {
          _statusText = 'Sunucu Hatası: ${response.statusCode} - $errorBody';
        });
      }
    } catch (e) {
      // (hata yönetimi aynı kalacak)
      setState(() {
        _statusText = 'Hata: Sunucuya bağlanılamadı. IP adresini ve sunucunun çalıştığını kontrol et.';
      });
    }
  }

  // (dispose ve build metodları aynı kalacak)
  @override
  void dispose() {
    _recorder.closeRecorder();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Text(_statusText, style: Theme.of(context).textTheme.headlineSmall, textAlign: TextAlign.center),
          const SizedBox(height: 40),
          ElevatedButton(
            onPressed: _isRecorderInitialized ? _toggleRecording : null,
            style: ElevatedButton.styleFrom(
              shape: const CircleBorder(),
              padding: const EdgeInsets.all(40),
              backgroundColor: _isRecording ? Colors.redAccent : Colors.deepPurple,
            ),
            child: Icon(_isRecording ? Icons.stop : Icons.mic, size: 60, color: Colors.white),
          ),
          const SizedBox(height: 40),
          if (_originalText.isNotEmpty)
            Expanded(
              child: SingleChildScrollView(
                child: Card(
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text('Orijinal Metin:', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 8),
                        Text(_originalText, style: Theme.of(context).textTheme.bodyLarge),
                        const Divider(height: 30, thickness: 1),
                        Text('Çeviri (${_targetLang.toUpperCase()}):', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 8),
                        Text(_translatedText, style: Theme.of(context).textTheme.bodyLarge),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}