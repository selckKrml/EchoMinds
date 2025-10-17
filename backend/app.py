import os
from flask import Flask, request, jsonify, send_file
from faster_whisper import WhisperModel
from elevenlabs.client import ElevenLabs
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from elevenlabs import save

# --- Kurulum ---
load_dotenv()
app = Flask(__name__)

# --- Modelleri ve İstemcileri Yükleme (Sadece bir kere) ---
print("Whisper 'large-v3' modeli yükleniyor... Bu işlem uzun sürebilir.")
model_stt = WhisperModel("large-v3", device="cpu", compute_type="int8")
print("Whisper modeli başarıyla yüklendi.")

elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
print("ElevenLabs istemcisi başarıyla başlatıldı.")

# --- API ENDPOINT'LERİ ---

@app.route("/")
def home():
    return "Gelişmiş Ses Uygulaması Sunucusu Çalışıyor!"

# --- Sekme 1: SPEECH TO TEXT Endpoint'i ---
@app.route("/stt", methods=["POST"])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "Ses dosyası bulunamadı"}), 400
    
    audio_file = request.files['audio']
    target_lang = request.form.get("target_lang", "en") # Varsayılan olarak İngilizce'ye çevir
    
    temp_filename = "temp_stt_input.wav"
    audio_file.save(temp_filename)

    try:
        # 1. Sesi Metne Çevir
        segments, _ = model_stt.transcribe(temp_filename)
        original_text = "".join(segment.text for segment in segments).strip()

        # 2. Metni Hedef Dile Çevir
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(original_text)

        return jsonify({
            "original_text": original_text,
            "translated_text": translated_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# --- Sekme 2: TEXT TO SPEECH Endpoint'i ---
@app.route("/tts", methods=["POST"])
def text_to_speech():
    data = request.json
    text = data.get("text")
    voice_id = data.get("voice_id", "pNInz6obpgDQGcFmaJgB") # Varsayılan: Adam
    target_lang = data.get("target_lang", "tr")

    if not text:
        return jsonify({"error": "Metin bulunamadı"}), 400

    try:
        # 1. Metni Gerekirse Çevir
        final_text = text
        if target_lang != "tr": # Eğer metin Türkçe değilse ve hedef dil farklıysa
            final_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        
        # 2. Metni Sese Dönüştür
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=final_text,
            model_id="eleven_multilingual_v2"
        )
        
        # 3. Sesi geçici bir dosyaya kaydet ve geri gönder
        output_filename = "temp_tts_output.wav"
        save(audio, output_filename)
        
        return send_file(output_filename, mimetype="audio/wav")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Sekme 3: SPEECH TO SPEECH Endpoint'i ---
@app.route("/s2s", methods=["POST"])
def speech_to_speech():
    if 'audio' not in request.files:
        return jsonify({"error": "Ses dosyası bulunamadı"}), 400

    audio_file = request.files['audio']
    voice_id = request.form.get("voice_id", "pNInz6obpgDQGcFmaJgB") # Varsayılan: Adam
    target_lang = request.form.get("target_lang", "en") # Varsayılan: İngilizce

    temp_filename = "temp_s2s_input.wav"
    audio_file.save(temp_filename)

    try:
        # Adım 1: Gelen Sesi Metne Çevir (STT)
        segments, _ = model_stt.transcribe(temp_filename)
        original_text = "".join(segment.text for segment in segments).strip()

        # Adım 2: Çevrilen Metni Hedef Dile Çevir
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(original_text)

        # Adım 3: Çevrilen Metni Sese Dönüştür (TTS)
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=translated_text,
            model_id="eleven_multilingual_v2"
        )
        
        output_filename = "temp_s2s_output.wav"
        save(audio, output_filename)
        
        return send_file(output_filename, mimetype="audio/wav")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


if __name__ == '__main__':
    # Mobil uygulama ile iletişim için 0.0.0.0 host'unu kullanmak önemlidir
    app.run(debug=True, host="0.0.0.0")