# Karaca Connect - Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
![Home Assistant](https://img.shields.io/badge/home--assistant-%230123.svg?style=for-the-badge&logo=home-assistant&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

[TR] Karaca Çaysever Robotea Pro Connect 4in1 akıllı çay makinesi için Home Assistant entegrasyonu.

[EN] Home Assistant custom integration for the Karaca Çaysever Robotea Pro Connect 4in1 smart tea maker.

---

## Türkçe

Bu entegrasyon Karaca Connect bulut API'sini kullanarak çay makinenizin durumunu Home Assistant'a aktarır ve cihaz modlarını kontrol etmenizi sağlar.

### Özellikler

- **Kurulum akışı:** Home Assistant arayüzünden e-posta ve şifre ile kurulum.
- **Cihaz seçimi:** Hesabınızda birden fazla desteklenen Karaca cihaz varsa kurulumda cihaz seçimi.
- **Mod kontrolü:** Su kaynatma, çay demleme, filtre kahve, mama suyu ve standby modları.
- **Güç anahtarı:** Cihazı varsayılan olarak su kaynatma modunda başlatma veya standby'a alma.
- **Durum sensörü:** `Su Kaynatılıyor`, `Su Hazır`, `Çay Demleniyor`, `Çay Hazır (Taze)`, `Kapalı` ve hata durumlarını enum sensör olarak sunar.
- **Tazelik takibi:** Çay hazır olduğunda tazelik/countdown bilgisi varsa durum `Çay Hazır (Taze)` olarak kalır.
- **Hata eşleme:** Su yok, hedef sıcaklık uygun değil, temizlik gerekli ve genel cihaz uyarıları sabit enum durumları olarak gösterilir.
- **Ayarlar:** Entegrasyon ayarlarından ad ön eki, güncelleme aralığı ve hata mesajının ekranda kalma süresi değiştirilebilir.
- **Kimlik doğrulama:** Token yenileme ve yeniden kimlik doğrulama akışı desteklenir.
- **Dil desteği:** Türkçe ve İngilizce çeviriler bulunur.
- **Diagnostics:** Sorun bildirimi için Home Assistant diagnostics desteği vardır.

### Kurulum

1. HACS arayüzünde sağ üst menüden **Custom repositories** bölümünü açın.
2. `https://github.com/yunusuztr/karaca-connect-ha` adresini ekleyin ve kategori olarak **Integration** seçin.
3. Entegrasyonu indirin ve Home Assistant'ı yeniden başlatın.
4. **Ayarlar > Cihazlar ve hizmetler > Entegrasyon ekle** bölümünden **Karaca Connect** aratın.
5. Karaca Connect hesabınızla giriş yapın ve kurulumu tamamlayın.

### Örnek Otomasyon

```yaml
alias: "Karaca: Su Hazır Bildirimi"
trigger:
  - platform: state
    entity_id: sensor.cay_makinesi_durumu
    from: "Su Kaynatılıyor"
    to: "Su Hazır"
action:
  - service: notify.notify
    data:
      title: "Karaca Çaysever"
      message: "Su hazır. Çayı demleyebilirsiniz."
```

---

## English

This integration connects to the Karaca Connect cloud API and exposes your smart tea maker in Home Assistant.

### Features

- **Config flow:** Set up from the Home Assistant UI with email and password.
- **Device selection:** Choose a supported Karaca device when multiple devices exist on the account.
- **Mode control:** Boiling water, tea brewing, filter coffee, baby water, and standby modes.
- **Power switch:** Start the device in boiling water mode or return it to standby.
- **Status sensor:** Exposes stable enum states such as `Su Kaynatılıyor`, `Su Hazır`, `Çay Demleniyor`, `Çay Hazır (Taze)`, `Kapalı`, and mapped error states.
- **Freshness handling:** When tea freshness/countdown data is active, the status remains `Çay Hazır (Taze)`.
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
