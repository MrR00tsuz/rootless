# Rootless 🌍
[![Watch the video](https://img.youtube.com/vi/jKKWZm3zC90/0.jpg)](https://www.youtube.com/watch?v=jKKWZm3zC90)

[English](#english) | [Türkçe](#türkçe)

## English

### Overview
Rootless is a web-based visualization tool that allows you to search and map devices indexed by Shodan on an interactive world map. It provides features for country-specific scanning, custom area searches, and data export capabilities.

### Features
- 🗺️ Interactive world map visualization
- 🔍 Custom area search with drawing tools
- 🌐 Country-specific grid scanning
- 📊 Real-time device statistics
- 💾 Data export in multiple formats
- 🌍 Multi-language support (EN/TR)

### Requirements
- Python 3.x
- MongoDB
- Flask
- Required Python packages (install via pip):
  ```
  flask
  pymongo
  shodan
  requests
  ```

### Installation
1. Clone the repository:
```bash
git clone https://github.com/MrR00tsuz/Rootless.git
cd Rootless
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure MongoDB:
- Make sure MongoDB is running on localhost:27017
- Create a database named "rootless"

4. **Important**: Update Cookie Information
You need to update the cookie information in `rootless.py`. Locate the following section:
```python
cookies = {"polito": "YOUR_COOKIE_HERE"}
```
Replace `YOUR_COOKIE_HERE` with your actual Shodan Maps cookie value.

5. Run the application:
```bash
python rootless.py
```

6. Access the application at `http://localhost:5000`

### Usage
1. Draw a rectangle on the map to search in a specific area
2. Enter search terms (e.g., "apache", "nginx", "country:TR")
3. Use the country scanning feature for systematic searches
4. Export found devices in various formats

### Note
⚠️ The cookie value is required for the application to work properly. You can obtain this by:
1. Visiting maps.shodan.io
2. Opening browser developer tools
3. Going to the Network tab
4. Finding a request to maps.shodan.io
5. Copying the 'polito' cookie value

---

## Türkçe

### Genel Bakış
Rootless, Shodan tarafından indekslenen cihazları interaktif dünya haritası üzerinde aramanıza ve görselleştirmenize olanak sağlayan web tabanlı bir araçtır. Ülke bazlı tarama, özel alan araması ve veri dışa aktarma özellikleri sunar.

### Özellikler
- 🗺️ İnteraktif dünya haritası görselleştirmesi
- 🔍 Çizim araçlarıyla özel alan araması
- 🌐 Ülke bazlı grid taraması
- 📊 Gerçek zamanlı cihaz istatistikleri
- 💾 Çoklu format desteği ile veri dışa aktarma
- 🌍 Çoklu dil desteği (TR/EN)

### Gereksinimler
- Python 3.x
- MongoDB
- Flask
- Gerekli Python paketleri (pip ile kurulum):
  ```
  flask
  pymongo
  shodan
  requests
  ```

### Kurulum
1. Depoyu klonlayın:
```bash
git clone https://github.com/MrR00tsuz/Rootless.git
cd Rootless
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. MongoDB Yapılandırması:
- MongoDB'nin localhost:27017'de çalıştığından emin olun
- "rootless" adında bir veritabanı oluşturun

4. **Önemli**: Cookie Bilgisini Güncelleme
`rootless.py` dosyasındaki cookie bilgisini güncellemeniz gerekmektedir. Şu bölümü bulun:
```python
cookies = {"polito": "COOKIE_DEGERINIZ"}
```
`COOKIE_DEGERINIZ` kısmını kendi Shodan Maps cookie değerinizle değiştirin.

5. Uygulamayı çalıştırın:
```bash
python rootless.py
```

6. Uygulamaya `http://localhost:5000` adresinden erişin

### Kullanım
1. Belirli bir alanda arama yapmak için haritada dikdörtgen çizin
2. Arama terimlerini girin (örn. "apache", "nginx", "country:TR")
3. Sistematik aramalar için ülke tarama özelliğini kullanın
4. Bulunan cihazları çeşitli formatlarda dışa aktarın

### Not
⚠️ Uygulamanın düzgün çalışması için cookie değeri gereklidir. Bu değeri şu şekilde elde edebilirsiniz:
1. maps.shodan.io adresini ziyaret edin
2. Tarayıcı geliştirici araçlarını açın
3. Ağ (Network) sekmesine gidin
4. maps.shodan.io'ya yapılan bir isteği bulun
5. 'polito' cookie değerini kopyalayın

### Lisans
MIT License 
