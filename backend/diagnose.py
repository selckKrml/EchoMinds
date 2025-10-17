import os
from huggingface_hub import constants

print("--- DİYAGNOSTİK TESTİ BAŞLATILDI ---")
print("\n[1] HUGGING FACE İLE İLGİLİ ORTAM DEĞİŞKENLERİ KONTROL EDİLİYOR...")

found_vars = False
# Sistemdeki tüm ortam değişkenlerini tara
for key, value in os.environ.items():
    if "HF_" in key or "HUGGINGFACE_" in key:
        print(f"  BULUNDU: {key} = {value}")
        found_vars = True

if not found_vars:
    print("  Hugging Face ile ilgili özel bir ortam değişkeni bulunamadı.")

print("\n[2] HUGGING FACE ÖNBELLEK VE YAPILANDIRMA KLASÖRLERİNİN YOLU KONTROL EDİLİYOR...")
# Kütüphanenin kendi sabitlerinden ayar dosyalarının yerini öğren
cache_dir = constants.HF_HUB_CACHE
config_dir = os.path.dirname(constants.HF_HUB_CONFIG_PATH)

print(f"  Önbellek (Cache) Klasörü: {cache_dir}")
print(f"  Yapılandırma (Config) Klasörü: {config_dir}")

print("\n--- DİYAGNOSTİK TESTİ TAMAMLANDI ---")
print("\nLÜTFEN YUKARIDAKİ TÜM ÇIKTIYI KOPYALAYIP GÖNDERİN.")