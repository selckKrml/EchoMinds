import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

print("--- GÜNCEL KÜTÜPHANE İLE SON TEST BAŞLATILDI ---")

load_dotenv()
api_token = os.getenv("HUGGINGFACE_API_TOKEN")

if not api_token:
    print("HATA: Hugging Face API anahtarı .env dosyasında bulunamadı!")
else:
    print("API Anahtarı başarıyla yüklendi.")

    try:
        # Güncel kütüphane ile doğru başlatma yöntemi
        client = InferenceClient(token=api_token)
        print("Client başarıyla başlatıldı.")

        audio_file_path = "ses.wav"
        print(f"'{audio_file_path}' dosyası metne çevriliyor... Lütfen bekleyin.")

        with open(audio_file_path, "rb") as f:
            audio_data = f.read()

        result_text = client.automatic_speech_recognition(
            audio_data,
            model="openai/whisper-large-v3",
        )

        print("\n--- BAŞARILI! ---")
        print("METİN ÇEVİRİSİ:")
        print(result_text)

    except Exception as e:
        print("\n--- BİR HATA OLUŞTU ---")
        print(f"HATA DETAYI: {e}")