import 'package:flutter/material.dart';
import 'config.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;
import 'dart:typed_data';
import 'package:audioplayers/audioplayers.dart';

class SpeechToSpeechTab extends StatefulWidget {
  const SpeechToSpeechTab({super.key});

  @override
  State<SpeechToSpeechTab> createState() => _SpeechToSpeechTabState();
}

class _SpeechToSpeechTabState extends State<SpeechToSpeechTab> {
  final FlutterSoundRecorder _recorder = FlutterSoundRecorder();
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isRecorderInitialized = false;
  bool _isRecording = false;
  String _statusText = 'Dönüşüm için ses kaydedin.';
  final String _audioFilePath = 's2s_audio.aac';

  final String _serverIp = '192.168.5.30'; // KENDİ IP ADRESİNİ YAZ
  String _selectedVoiceId = "pNInz6obpgDQGcFmaJgB"; // Varsayılan: Adam
  String _targetLang = 'en'; // Varsayılan: İngilizce

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
    setState(() => _isRecorderInitialized = true);
  }

  Future<void> _toggleRecording() async {
    if (!_isRecorderInitialized) return;
    if (_isRecording) {
      await _recorder.stopRecorder();
      setState(() {
        _statusText = '✅ Kayıt tamamlandı. Dönüşüm yapılıyor...';
        _isRecording = false;
      });
      _uploadAndConvert();
    } else {
      setState(() {
        _statusText = '🔴 Kayıt yapılıyor...';
        _isRecording = true;
      });
      await _recorder.startRecorder(toFile: _audioFilePath, codec: Codec.aacADTS);
    }
  }

  Future<void> _uploadAndConvert() async {
    setState(() => _statusText = '🎤 Sesten sese dönüşüm yapılıyor...');
    try {
      var uri = Uri.parse('http://$_serverIp:5000/s2s');
      var request = http.MultipartRequest('POST', uri)
        ..fields['target_lang'] = _targetLang
        ..fields['voice_id'] = _selectedVoiceId
        ..files.add(await http.MultipartFile.fromPath('audio', _audioFilePath));

      var response = await request.send();

      if (response.statusCode == 200) {
        final Uint8List audioBytes = await response.stream.toBytes();
        await _audioPlayer.play(BytesSource(audioBytes));
        setState(() => _statusText = '✅ Dönüşüm tamamlandı ve oynatılıyor!');
      } else {
        setState(() => _statusText = 'Sunucu Hatası: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _statusText = 'Hata: Sunucuya bağlanılamadı.');
    }
  }

  @override
  void dispose() {
    _recorder.closeRecorder();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
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
              backgroundColor: _isRecording ? Colors.redAccent : Colors.blueAccent,
            ),
            child: Icon(_isRecording ? Icons.stop : Icons.mic, size: 60, color: Colors.white),
          ),
          // SES VE DİL SEÇİMİ EKLENECEK
        ],
      ),
    );
  }
}