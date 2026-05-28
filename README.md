# Karaca Connect - Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
![Home Assistant](https://img.shields.io/badge/home--assistant-%230123.svg?style=for-the-badge&logo=home-assistant&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

[TR] Karaca Caysever Robotea Pro Connect 4in1 akilli cay makinesi icin Home Assistant entegrasyonu.`n[EN] Home Assistant custom integration for the Karaca Caysever Robotea Pro Connect 4in1 smart tea maker.

---

## Turkce

Bu entegrasyon Karaca Connect bulut API'sini kullanarak cay makinenizin durumunu Home Assistant'a aktarir ve cihaz modlarini kontrol etmenizi saglar.

### Ozellikler

- **Kurulum akisi:** Home Assistant arayuzunden e-posta ve sifre ile kurulum.
- **Cihaz secimi:** Hesabinizda birden fazla desteklenen Karaca cihaz varsa kurulumda cihaz secimi.
- **Mod kontrolu:** Su kaynatma, cay demleme, filtre kahve, mama suyu ve standby modlari.
- **Guc anahtari:** Cihazi varsayilan olarak su kaynatma modunda baslatma veya standby'a alma.
- **Durum sensoru:** `Su Kaynatiliyor`, `Su Hazir`, `Cay Demleniyor`, `Cay Hazir (Taze)`, `Kapali` ve hata durumlarini enum sensor olarak sunar.
- **Tazelik takibi:** Cay hazir oldugunda tazelik/countdown bilgisi varsa durum `Cay Hazir (Taze)` olarak kalir.
- **Hata esleme:** Su yok, hedef sicaklik uygun degil, temizlik gerekli ve genel cihaz uyarilari sabit enum durumlari olarak gosterilir.
- **Ayarlar:** Entegrasyon ayarlarindan ad on eki, guncelleme araligi ve hata mesajinin ekranda kalma suresi degistirilebilir.
- **Kimlik dogrulama:** Token yenileme ve yeniden kimlik dogrulama akisi desteklenir.
- **Dil destegi:** Turkce ve Ingilizce ceviriler bulunur.
- **Diagnostics:** Sorun bildirimi icin Home Assistant diagnostics destegi vardir.

### Kurulum

1. HACS arayuzunde sag ust menuden **Custom repositories** bolumunu acin.
2. `https://github.com/yunusuztr/karaca-connect-ha` adresini ekleyin ve kategori olarak **Integration** secin.
3. Entegrasyonu indirin ve Home Assistant'i yeniden baslatin.
4. **Ayarlar > Cihazlar ve hizmetler > Entegrasyon ekle** bolumunden **Karaca Connect** aratin.
5. Karaca Connect hesabinizla giris yapin ve kurulumu tamamlayin.

### Ornek Otomasyon

```yaml
alias: "Karaca: Su Hazir Bildirimi"
trigger:
  - platform: state
    entity_id: sensor.cay_makinesi_durumu
    from: "Su Kaynatiliyor"
    to: "Su Hazir"
action:
  - service: notify.notify
    data:
      title: "Karaca Caysever"
      message: "Su hazir. Cayi demleyebilirsiniz."
```

---

## English

This integration connects to the Karaca Connect cloud API and exposes your smart tea maker in Home Assistant.

### Features

- **Config flow:** Set up from the Home Assistant UI with email and password.
- **Device selection:** Choose a supported Karaca device when multiple devices exist on the account.
- **Mode control:** Boiling water, tea brewing, filter coffee, baby water, and standby modes.
- **Power switch:** Start the device in boiling water mode or return it to standby.
- **Status sensor:** Exposes stable enum states such as `Su Kaynatiliyor`, `Su Hazir`, `Cay Demleniyor`, `Cay Hazir (Taze)`, `Kapali`, and mapped error states.
- **Freshness handling:** When tea freshness/countdown data is active, the status remains `Cay Hazir (Taze)`.
- **Error mapping:** Water empty, invalid target temperature, cleaning required, and generic device warnings are exposed as stable enum states.
- **Options flow:** Configure name prefix, polling interval, and how long command errors remain visible.
- **Authentication:** Refresh-token handling and reauthentication support.
- **Translations:** Turkish and English UI translations.
- **Diagnostics:** Home Assistant diagnostics support for issue reports.

### Installation

1. Open **HACS**, then **Custom repositories**.
2. Add `https://github.com/yunusuztr/karaca-connect-ha` and select **Integration**.
3. Download the integration and restart Home Assistant.
4. Go to **Settings > Devices & Services > Add Integration** and search for **Karaca Connect**.
5. Sign in with your Karaca Connect account and finish setup.

---

## License & Disclaimer

This is a community-driven custom integration and is not affiliated with Karaca. Product names, logos, and brands belong to their respective owners.
