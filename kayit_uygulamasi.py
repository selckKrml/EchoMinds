import tkinter as tk
from tkinter import scrolledtext, OptionMenu, StringVar
import threading
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write, read as read_wav # wav dosyasını okumak için eklendi
from faster_whisper import WhisperModel
from elevenlabs import save # 'play' yerine 'save' fonksiyonunu kullanacağız
from elevenlabs.client import ElevenLabs
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os
import time

# --- UYGULAMA AYARLARI ---
MODEL_SIZE = "large-v3"
SAMPLE_RATE = 16000
RECORDING_FILENAME = "sound.wav"
TTS_OUTPUT_FILENAME = "tts_output.wav" # Oluşturulan sesin kaydedileceği dosya

ELEVENLABS_VOICES = {
    "Adam (Amerikan, Derin)": "pNInz6obpgDQGcFmaJgB",
    "Rachel (Amerikan, Sakin)": "21m00Tcm4TlvDq8ikWAM",
    "Antoni (Amerikan, Genç)": "ErXwobaYiN019P7PKGPO",
    "Dorothy (İngiliz, Yaşlı)": "ThT5KcBeYPX3keUQqHPh",
    "Mimi (Fransız, Genç)": "zrHiDhphv9JoVUBF1dZz",
    "Giovanni (İtalyan, Genç)": "zcAOhNBS3c14rBihAFp1",
}

LANGUAGES = {
    "Türkçe": "tr",
    "İngilizce": "en",
    "Almanca": "de",
    "İspanyolca": "es",
    "Fransızca": "fr",
}

# --- API İSTEMCİLERİNİ VE MODELİ YÜKLEME ---
load_dotenv()

print(f"'{MODEL_SIZE}' modeli yükleniyor. Bu işlem uzun sürebilir...")
try:
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    print(f"'{MODEL_SIZE}' modeli başarıyla yüklendi.")
except Exception as e:
    print(f"Whisper modeli yüklenirken hata oluştu: {e}")
    model = None

try:
    elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    print("ElevenLabs istemcisi başarıyla başlatıldı.")
except Exception as e:
    print(f"ElevenLabs istemcisi başlatılamadı! API anahtarını .env dosyasında kontrol et. Hata: {e}")
    elevenlabs_client = None

try:
    translator = GoogleTranslator(source='auto', target='tr')
    print("Çeviri motoru hazır.")
except Exception as e:
    print(f"Çeviri motoru başlatılamadı: {e}")
    translator = None

# --- UYGULAMA DEĞİŞKENLERİ ---
is_recording = False
audio_frames = []

# --- ANA FONKSİYONLAR ---
def record_audio_thread():
    global audio_frames
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
        while is_recording:
            audio_chunk, _ = stream.read(SAMPLE_RATE)
            audio_frames.append(audio_chunk)

def transcribe_audio_thread():
    if not model:
        update_status("HATA: Whisper modeli yüklenemedi!")
        return
    update_status("✍️ Metne çevriliyor... Bu işlem YAVAŞ olabilir, lütfen bekleyin.")
    try:
        segments, _ = model.transcribe(RECORDING_FILENAME, beam_size=5)
        transcribed_text = "".join(segment.text for segment in segments).strip()
        print("\n--- ÇEVİRİ SONUCU --- \n" + transcribed_text)
        text_area.delete('1.0', tk.END)
        text_area.insert('1.0', transcribed_text)
        update_status("✅ STT tamamlandı! Aşağıdaki butona basarak metni seslendirebilirsiniz.")
        speak_stt_button.config(state=tk.NORMAL)
    except Exception as e:
        update_status(f"Çeviri sırasında hata: {e}")
    record_button.config(state=tk.NORMAL)

def toggle_recording():
    global is_recording, audio_frames
    if is_recording:
        is_recording = False
        record_button.config(text="Kayda Başla", bg="green")
        update_status("✅ Kayıt tamamlandı. Dosya kaydediliyor...")
        time.sleep(0.1)
        recording = np.concatenate(audio_frames, axis=0)
        write(RECORDING_FILENAME, SAMPLE_RATE, (recording * 32767).astype(np.int16))
        record_button.config(state=tk.DISABLED)
        speak_stt_button.config(state=tk.DISABLED)
        threading.Thread(target=transcribe_audio_thread).start()
    else:
        is_recording = True
        audio_frames = []
        record_button.config(text="Kaydı Durdur", bg="red")
        update_status("🔴 Kayıt yapılıyor... Durdurmak için tekrar basın.")
        threading.Thread(target=record_audio_thread).start()

def speak_thread(text, voice_id, lang_code):
    if not elevenlabs_client or not translator:
        update_status("HATA: Gerekli birimler başlatılamadı!")
        set_all_buttons_state(tk.NORMAL)
        return
    try:
        final_text = text
        if lang_code != "tr":
            update_status(f"✍️ Metin '{lang_code}' diline çevriliyor...")
            translator.target = lang_code
            final_text = translator.translate(text)
            print(f"Çevrilen Metin ({lang_code}): {final_text}")
        
        update_status("🔊 Ses oluşturuluyor...")
        audio = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=final_text,
            model_id="eleven_multilingual_v2"
        )
        
        # --- BU BÖLÜM TAMAMEN DEĞİŞTİRİLDİ ---
        # 1. Adım: Sesi dosyaya kaydet
        save(audio, TTS_OUTPUT_FILENAME)
        
        # 2. Adım: Kaydedilen dosyayı oku ve sounddevice ile oynat
        update_status("🎧 Ses oynatılıyor...")
        samplerate, data = read_wav(TTS_OUTPUT_FILENAME)
        sd.play(data, samplerate)
        sd.wait() # Sesin bitmesini bekle
        # --- DÜZELTME BİTTİ ---
        
        update_status("✅ Seslendirme tamamlandı!")
    except Exception as e:
        update_status(f"Seslendirme hatası: {e}")
    finally:
        set_all_buttons_state(tk.NORMAL)

def handle_speak():
    text_to_speak = text_area.get("1.0", tk.END).strip()
    if not text_to_speak:
        update_status("Lütfen metin kutusuna bir şeyler yazın.")
        return
    voice_name = selected_voice.get()
    voice_id = ELEVENLABS_VOICES[voice_name]
    lang_name = selected_language.get()
    lang_code = LANGUAGES[lang_name]
    set_all_buttons_state(tk.DISABLED)
    threading.Thread(target=speak_thread, args=(text_to_speak, voice_id, lang_code)).start()
    
def update_status(message):
    status_label.config(text=message)
    print(f"DURUM: {message}")

def set_all_buttons_state(state):
    record_button.config(state=state)
    speak_button.config(state=state)
    if text_area.get("1.0", tk.END).strip():
        speak_stt_button.config(state=state)

# --- GRAFİK ARAYÜZÜ (Değişiklik yok) ---
root = tk.Tk()
root.title("Gelişmiş Ses Uygulaması")
root.geometry("600x450")
top_frame = tk.Frame(root)
top_frame.pack(pady=5)
text_frame = tk.Frame(root)
text_frame.pack(pady=5, padx=10, fill="x")
controls_frame = tk.Frame(root)
controls_frame.pack(pady=10)
status_label = tk.Label(top_frame, text="Uygulama hazır.", pady=5, font=("Helvetica", 12))
status_label.pack()
record_button = tk.Button(top_frame, text="Kayda Başla", font=("Helvetica", 14, "bold"),
                          bg="green", fg="white", command=toggle_recording, padx=20, pady=10)
record_button.pack()
text_area = scrolledtext.ScrolledText(text_frame, height=8, font=("Helvetica", 11))
text_area.pack(fill="x")
tk.Label(controls_frame, text="Ses Seçimi:").grid(row=0, column=0, padx=5, sticky="w")
selected_voice = StringVar(root)
selected_voice.set(list(ELEVENLABS_VOICES.keys())[0])
voice_menu = OptionMenu(controls_frame, selected_voice, *ELEVENLABS_VOICES.keys())
voice_menu.grid(row=0, column=1, padx=5, sticky="ew")
tk.Label(controls_frame, text="Hedef Dil:").grid(row=1, column=0, padx=5, sticky="w")
selected_language = StringVar(root)
selected_language.set(list(LANGUAGES.keys())[0])
language_menu = OptionMenu(controls_frame, selected_language, *LANGUAGES.keys())
language_menu.grid(row=1, column=1, padx=5, sticky="ew")
speak_button = tk.Button(controls_frame, text="Yazılan Metni Konuş", command=handle_speak)
speak_button.grid(row=2, column=0, pady=10, padx=5)
speak_stt_button = tk.Button(controls_frame, text="Kaydedilen Sesi Konuş", command=handle_speak, state=tk.DISABLED)
speak_stt_button.grid(row=2, column=1, pady=10, padx=5)
controls_frame.columnconfigure(1, weight=1)
root.mainloop()