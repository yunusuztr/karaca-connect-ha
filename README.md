# ☕ Karaca Connect - Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
![Home Assistant](https://img.shields.io/badge/home--assistant-%230123.svg?style=for-the-badge&logo=home-assistant&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

[TR] Karaca Çaysever Robotea Pro Connect 4in1 akıllı çay makinesinin Home Assistant entegrasyonu.  
[EN] Home Assistant custom integration for the Karaca Çaysever Robotea Pro Connect 4in1 smart tea maker.

---

## 🇹🇷 Türkçe Kullanım Kılavuzu

Bu entegrasyon, Karaca Connect bulut API'sini kullanarak çay makinenizin durumunu (sıcaklık, kaynama aşaması, aktif mod vb.) Home Assistant'a aktarır ve cihazı tamamen kontrol etmenizi sağlar.

### 🌟 Özellikler
- **Mod Kontrolü (select):** Çay demleme, su kaynatma, filtre kahve, mama suyu hazırlama veya standby (kapatma) modlarını doğrudan HA arayüzünden seçip tetikleyebilirsiniz.
- **Güç Şalteri (switch):** Tek bir tıkla makineyi çalıştırabilir (varsayılan olarak su kaynatma modunda açılır) veya standby moduna alarak tamamen kapatabilirsiniz.
- **Durum Takibi (sensor):** Cihazın anlık aşamasını ("Su Kaynatılıyor", "Su Hazır", "Çay Demleniyor", "Kapalı") Türkçe olarak takip edebilir, countdown (geri sayım) ve freshness (tazelik süresi) verilerini extra attributes olarak görebilirsiniz.
- **Güvenli Kimlik Doğrulama:** E-posta ve şifreniz yerel olarak şifrelenmiş HA .storage sisteminde saklanır. JWT token'lar otomatik yenilenir.
- **Hata ve Uyarı Yönetimi (Sensor Üzerinde):** Fiziksel kurallara uymayan hatalı bir komut gönderildiğinde (örn. mevcut su sıcaklığının altında bir Mama Suyu sıcaklığı seçildiğinde veya haznede su yokken çalıştırma denendiğinde) Karaca sunucularından dönen Türkçe hata uyarısı anlık olarak `sensor.cay_makinesi_durumu` sensörünün durumu (state) olarak gösterilir (Örn: `"Hata: Belirlenen hedef sıcaklık, mevcut su sıcaklığının altındadır."`). Bu durum 15 saniye boyunca ekranda kalarak otomasyon tetiklemelerinizi kolaylaştırır, ardından cihazın gerçek fiziksel durumuna otomatik olarak geri döner. Ayrıca hata mesajı extra attributes altındaki `last_error` alanında da saklanır.

### 🔌 Kurulum
1. HACS arayüzüne gidin, sağ üstteki üç noktaya tıklayıp **"Custom Repositories"** seçeneğini seçin.
2. Bu deponun URL adresini (`https://github.com/yunusuztr/karaca-connect-ha`) ekleyin ve kategori olarak **"Integration"** seçin.
3. HACS üzerinden indirdikten sonra Home Assistant'ı yeniden başlatın.
4. **Ayarlar > Cihazlar ve Hizmetler > Entegrasyon Ekle** kısmından **Karaca Connect** entegrasyonunu aratın.
5. Kullanıcı adı, şifre ve çaycınız için istediğiniz **özel isim ön ekini** girerek kurulumu tamamlayın.

### 🔔 Otomasyon ve Bildirim Örnekleri
Su kaynadığında veya çay demlendiğinde telefonunuza bildirim göndermek için aşağıdaki YAML otomasyon şablonunu kullanabilirsiniz:

```yaml
alias: "Çaycı: Su Kaynadı Bildirimi"
trigger:
  - platform: state
    entity_id: sensor.cay_makinesi_durumu
    from: "Su Kaynatılıyor"
    to: "Su Hazır"
action:
  - service: notify.notify
    data:
      title: "☕ Karaca Çaysever"
      message: "Su kaynadı! Çayınızı demleyebilirsiniz."
  - service: tts.speak
    target:
      entity_id: tts.google_en_com
    data:
      media_player_entity_id: media_player.hoparlor1
      message: "Su hazır, çayı demliyorum."
```

---

## 🇬🇧 English Documentation

This integration connects directly to your Karaca Connect account and registers your smart tea maker under Home Assistant.

### 🌟 Features
- **Mode Selection (select):** Select between Standby (off), Filter Coffee, Boiling Water, Tea Brewing, and Baby Food modes.
- **Master Power Switch (switch):** Easily turn the device ON (defaults to Boiling Water) or OFF.
- **Telemetry Sensors (sensor):** Tracks real-time friendly status (e.g. Boiling, Boiled, Standby, Tea Brewing) and exposes freshness countdowns as attributes.
- **Sensor-Level Error & Warning Management:** Any command violating physical rules (e.g., trying to boil water when empty, or setting a target baby food temperature below the current water temperature) will instantly set the `sensor.cay_makinesi_durumu` state to `"Hata: {error_description}"`. This state persists for 15 seconds (perfect for triggering Home Assistant automations) before automatically reverting back to the actual physical state of the device. The warning is also exposed under the `last_error` extra state attribute.

### 🔌 Installation
1. Go to **HACS**, select **Custom Repositories** from the top-right menu.
2. Paste this repository URL (`https://github.com/yunusuztr/karaca-connect-ha`) and choose **Integration** as category.
3. Download it and restart Home Assistant.
4. Go to **Settings -> Devices & Services -> Add Integration**, search for **Karaca Connect**.
5. Log in with your email and password, customize your device name prefix, and enjoy!

---

## ⚖️ License & Disclaimer

This is a community-driven open-source integration. All product names, logos, and brands are property of their respective owners (Karaca Züccaciye A.Ş.). Interoperability is achieved using cloud REST APIs captured under personal-use reverse engineering guidelines.