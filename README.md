# EchoMinds: Gelişmiş Ses Dönüşüm Uygulaması

![Flutter](https://img.shields.io/badge/Flutter-%2302569B.svg?style=for-the-badge&logo=Flutter&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

Flutter ile geliştirilmiş modern bir mobil arayüz ile Python (Flask) üzerinde çalışan güçlü bir yapay zeka sunucusunu birleştiren bu proje; konuşmayı metne, metni konuşmaya ve bir dildeki konuşmayı başka bir dildeki konuşmaya dönüştürme yeteneklerine sahiptir.

## 🎞️ Uygulama Demosu

*(Buraya uygulamanın ekran kaydını alıp oluşturduğun bir GIF veya kısa bir video linki eklemen, projenin çok daha etkileyici görünmesini sağlar.)*

![Uygulama Gifi](link-buraya-gelecek.gif)

## ✨ Özellikler

-   🗣️ **Konuşmadan Metne (Speech to Text):**
    -   Mikrofon aracılığıyla ses kaydı alır.
    -   `faster-whisper (large-v3)` modelini kullanarak sesi yüksek doğrulukla metne çevirir.
    -   Çevrilen metni, seçilen hedef dile anında tercüme eder.
    -   Çevrilen orijinal metinleri daha sonra kullanmak üzere yerel veritabanına (SQLite) kaydeder.

-   ✍️ **Metinden Konuşmaya (Text to Speech):**
    -   Daha önce kaydedilmiş metinleri listeler ve seçme imkanı sunar.
    -   Manuel olarak metin girilmesine olanak tanır.
    -   `ElevenLabs` API'sini kullanarak metni birden çok dilde ve farklı ses seçenekleriyle doğal bir şekilde seslendirir.
    -   Kaydedilmiş metinleri silme işlevselliği sunar.

-   🎤 **Sesten Sese (Speech to Speech):**
    -   Bir dilde ses kaydı alır.
    -   Kaydı önce metne çevirir, ardından bu metni hedeflenen dile tercüme eder.
    -   Son olarak, tercüme edilmiş metni hedeflenen dilde ve seçilen bir sesle yeniden seslendirir.

## 🛠️ Teknoloji Mimarisi

### **Backend (Sunucu)**
-   **Dil & Framework:** Python 3, Flask
-   **Konuşmadan Metne:** `faster-whisper` (CPU üzerinde `large-v3` modeli)
-   **Metinden Konuşmaya:** `elevenlabs-python` (ElevenLabs API Entegrasyonu)
-   **Dil Çevirisi:** `deep-translator` (Google Translate API)

### **Frontend (Mobil Uygulama)**
-   **Framework:** Flutter
-   **Dil:** Dart
-   **Ağ İstekleri:** `http`
-   **Ses Kaydı:** `flutter_sound`
-   **Ses Oynatma:** `audioplayers`
-   **Yerel Veritabanı:** `sqflite` & `path_provider`
-   **İzin Yönetimi:** `permission_handler`

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### **Gereksinimler**
-   Python 3.8+
-   Flutter SDK
-   Git

### **1. Backend Sunucusunu Kurma**

```bash
# 1. Proje klonlandıktan sonra backend klasörüne gidin
cd backend

# 2. Bir sanal ortam (virtual environment) oluşturun ve aktive edin
python -m venv venv
# Windows için:
.\venv\Scripts\activate

# 3. Gerekli Python kütüphanelerini yükleyin
pip install -r requirements.txt

# 4. API anahtarınızı ayarlayın
# backend klasörü içinde .env adında bir dosya oluşturun ve içine
# ElevenLabs API anahtarınızı aşağıdaki gibi ekleyin:
# ELEVENLABS_API_KEY="sk_xxxxxxxxxxxxxxxxxxxxxxxxxx"

# 5. Sunucuyu başlatın
flask run --host=0.0.0.0
```

### **2. Frontend Mobil Uygulamasını Kurma**

```bash
# 1. Terminalde projenin frontend klasörüne gidin
cd frontend

# 2. Sunucu IP Adresini Ayarlayın
# /lib/config.dart dosyasını açın ve 'serverIp' değişkenini
# backend sunucusunun çalıştığı bilgisayarın yerel IP adresi ile güncelleyin.
# (Örn: const String serverIp = '192.168.1.45';)

# 3. Flutter paketlerini yükleyin
flutter pub get

# 4. Uygulamayı bir emülatörde veya gerçek bir cihazda çalıştırın
flutter run
```

## 📈 Gelecek Planları

-   [ ] Daha fazla dil ve ses seçeneği eklemek.
-   [ ] Seslendirme hızını ve tonunu ayarlama seçenekleri sunmak.
-   [ ] Kullanıcıların kendi ElevenLabs API anahtarlarını uygulama içinden girmesine olanak tanımak.
-   [ ] Docker ile projenin kurulumunu kolaylaştırmak.

---

Bu proje, farklı yapay zeka servislerini bir araya getirme ve full-stack bir uygulama geliştirme pratiği olarak oluşturulmuştur.
