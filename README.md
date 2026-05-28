# ğŸµ Karaca Connect - Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
![Home Assistant](https://img.shields.io/badge/home--assistant-%230123.svg?style=for-the-badge&logo=home-assistant&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

[TR] Karaca Ã‡aysever Robotea Pro Connect 4in1 akÄ±llÄ± Ã§ay makinesini Home Assistant entegrasyonu.  
[EN] Home Assistant custom integration for the Karaca Ã‡aysever Robotea Pro Connect 4in1 smart tea maker.

---

## ğŸ‡¹ğŸ‡· TÃ¼rkÃ§e KullanÄ±m KÄ±lavuzu

Bu entegrasyon, Karaca Connect bulut API'sini kullanarak Ã§ay makinenizin durumunu (sÄ±caklÄ±k, kaynama aÅŸamasÄ±, aktif mod vb.) Home Assistant'a aktarÄ±r ve cihazÄ± tamamen kontrol etmenizi saÄŸlar.

### ğŸŒŸ Ã–zellikler
- **Mod KontrolÃ¼ (select):** Ã‡ay demleme, su kaynatma, filtre kahve, mama suyu hazÄ±rlama veya standby (kapatma) modlarÄ±nÄ± doÄŸrudan HA arayÃ¼zÃ¼nden seÃ§ip tetikleyebilirsiniz.
- **GÃ¼Ã§ Åalteri (switch):** Tek bir tÄ±kla makineyi Ã§alÄ±ÅŸtÄ±rabilir (varsayÄ±lan olarak su kaynatma modunda aÃ§Ä±lÄ±r) veya standby moduna alarak tamamen kapatabilirsiniz.
- **Durum Takibi (sensor):** CihazÄ±n anlÄ±k aÅŸamasÄ±nÄ± ("Su KaynatÄ±lÄ±yor", "Su HazÄ±r", "Ã‡ay Demleniyor", "KapalÄ±") TÃ¼rkÃ§e olarak takip edebilir, countdown (geri sayÄ±m) ve freshness (tazelik sÃ¼resi) verilerini extra attributes olarak gÃ¶rebilirsiniz.
- **GÃ¼venli Kimlik DoÄŸrulama:** E-posta ve ÅŸifreniz yerel olarak ÅŸifrelenmiÅŸ HA .storage sisteminde saklanÄ±r. JWT token'lar otomatik yenilenir.

### ğŸ”Œ Kurulum
1. HACS arayÃ¼zÃ¼ne gidin, saÄŸ Ã¼stteki Ã¼Ã§ noktaya tÄ±klayÄ±p **"Custom Repositories"** seÃ§eneÄŸini seÃ§in.
2. Bu deponun URL adresini ekleyin ve kategori olarak **"Integration"** seÃ§in.
3. HACS Ã¼zerinden indirdikten sonra Home Assistant'Ä± yeniden baÅŸlatÄ±n.
4. **Ayarlar > Cihazlar ve Hizmetler > Entegrasyon Ekle** kÄ±smÄ±ndan **Karaca Connect** entegrasyonunu aratÄ±n.
5. KullanÄ±cÄ± adÄ±, ÅŸifre ve Ã§aycÄ±nÄ±z iÃ§in istediÄŸiniz **Ã¶zel isim Ã¶n ekini** girerek kurulumu tamamlayÄ±n.

### ğŸ”” Otomasyon ve Bildirim Ã–rnekleri
Su kaynadÄ±ÄŸÄ±nda veya Ã§ay demlendiÄŸinde telefonunuza bildirim gÃ¶ndermek iÃ§in aÅŸaÄŸÄ±daki YAML otomasyon ÅŸablonunu kullanabilirsiniz:

`yaml
alias: "Ã‡aycÄ±: Su KaynadÄ± Bildirimi"
trigger:
  - platform: state
    entity_id: sensor.cay_makinesi_durumu
    from: "Su KaynatÄ±lÄ±yor"
    to: "Su HazÄ±r"
action:
  - service: notify.notify
    data:
      title: "ğŸµ Karaca Ã‡aysever"
      message: "Su kaynadÄ±! Ã‡ayÄ±nÄ±zÄ± demleyebilirsiniz."
  - service: tts.speak
    target:
      entity_id: tts.google_en_com
    data:
      media_player_entity_id: media_player.hoparlor1
      message: "Su hazÄ±r, Ã§ayÄ± demliyorum."
`

---

## ğŸ‡¬ğŸ‡§ English Documentation

This integration connects directly to your Karaca Connect account and registers your smart tea maker under Home Assistant.

### ğŸŒŸ Features
- **Mode Selection (select):** Select between Standby (off), Filter Coffee, Boiling Water, Tea Brewing, and Baby Food modes.
- **Master Power Switch (switch):** Easily turn the device ON (defaults to Boiling Water) or OFF.
- **Telemetry Sensors (sensor):** Tracks real-time friendly status (e.g. Boiling, Boiled, Standby, Tea Brewing) and exposes freshness countdowns as attributes.

### ğŸ”Œ Installation
1. Go to **HACS**, select **Custom Repositories** from the top-right menu.
2. Paste this repository URL and choose **Integration** as category.
3. Download it and restart Home Assistant.
4. Go to **Settings -> Devices & Services -> Add Integration**, search for **Karaca Connect**.
5. Log in with your email and password, customize your device name prefix, and enjoy!

---

## âš–ï¸ License & Disclaimer

This is a community-driven open-source integration. All product names, logos, and brands are property of their respective owners (Karaca ZÃ¼ccaciye A.Å.). Interoperability is achieved using cloud REST APIs captured under personal-use reverse engineering guidelines.