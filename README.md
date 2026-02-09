# Sistem Peringatan Dini Banjir (Early Warning Flood System)

Sistem monitoring real-time untuk mendeteksi dini potensi banjir berdasarkan data ketinggian air, curah hujan, dan kecepatan angin dari sensor Arduino.

## Fitur Utama

✅ **Real-time Monitoring**
- Tampilan data sensor secara real-time
- Update otomatis setiap 5 detik
- Antarmuka yang intuitif dan responsif

✅ **Peringatan & Alert**
- Sistem tingkat peringatan (NORMAL, ALERT, WARNING, EMERGENCY)
- Notifikasi audio saat kondisi darurat
- Indikator visual yang jelas

✅ **Visualisasi Data**
- Grafik ketinggian air
- Grafik curah hujan
- Grafik kecepatan angin
- Grafik status peringatan

✅ **Riwayat Data**
- Tabel lengkap semua data sensor
- Statistik lengkap (rata-rata, max, min)
- Limit 100 data terbaru ditampilkan

✅ **Export Data**
- Export ke Excel (.xlsx)
- Export ke PDF dengan format laporan
- Data dapat diunduh kapan saja

✅ **Pengaturan Ambang Batas**
- Sesuaikan threshold untuk setiap sensor
- Pengaturan disimpan di database
- Konfigurasi dinamis tanpa restart

## Instalasi

### 1. Prasyarat
- Python 3.8+
- Arduino dengan sensor
- USB cable untuk menghubungkan Arduino

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Arduino
- Upload sketch dari file `arduino_sketch.ino` ke Arduino
- Hubungkan sensor ke pin analog:
  - A0: Sensor Ketinggian Air
  - A1: Sensor Curah Hujan
  - A2: Sensor Kecepatan Angin

### 4. Mulai Server
```bash
python app.py
```

Server akan berjalan di `http://localhost:5000`

### 5. (Opsional) Mulai Arduino Client
Untuk pengiriman otomatis dari Arduino:
```bash
python arduino_client.py
```

## Penggunaan

### Akses Web Interface
Buka browser dan navigasi ke `http://localhost:5000`

### Mengirim Data Manual
Gunakan API endpoint:
```bash
curl -X POST http://localhost:5000/api/data/add \
  -H "Content-Type: application/json" \
  -d '{"water_height": 50, "rainfall": 75, "wind_speed": 30}'
```

### Export Data
- Klik tombol "Export Excel" untuk unduh data dalam format .xlsx
- Klik tombol "Export PDF" untuk unduh laporan dalam format .pdf

## API Endpoints

### GET /api/data/latest
Dapatkan data sensor terbaru
```json
{
  "id": 1,
  "timestamp": "2026-02-09 10:30:45",
  "water_height": 45.5,
  "rainfall": 75.2,
  "wind_speed": 25.0,
  "alert_status": "NORMAL"
}
```

### GET /api/data/history?limit=100
Dapatkan riwayat data (default 100 records)

### POST /api/data/add
Kirim data sensor baru
```json
{
  "water_height": 45.5,
  "rainfall": 75.2,
  "wind_speed": 25.0
}
```

### GET /api/settings
Dapatkan pengaturan ambang batas

### POST /api/settings/update
Update ambang batas
```json
{
  "water_height_threshold": 50.0,
  "rainfall_threshold": 100.0,
  "wind_speed_threshold": 40.0
}
```

### GET /api/stats
Dapatkan statistik lengkap data

### GET /api/export/excel
Download data dalam format Excel

### GET /api/export/pdf
Download laporan dalam format PDF

## Tingkat Peringatan

| Status | Kondisi | Tindakan |
|--------|---------|----------|
| **NORMAL** | Semua parameter aman | Tetap monitor |
| **ALERT** | Satu parameter mendekati threshold | Bersiaplah |
| **WARNING** | Dua atau lebih parameter tinggi | Siaga |
| **EMERGENCY** | Kondisi darurat, banjir akan terjadi | SEGERA EVAKUASI |

## Struktur Direktori

```
monitoring/
├── app.py                 # Backend Flask
├── arduino_client.py      # Klien Arduino (optional)
├── arduino_sketch.ino     # Kode Arduino
├── requirements.txt       # Dependencies Python
├── flood_data.db         # Database SQLite (otomatis dibuat)
├── templates/
│   └── index.html        # Frontend HTML
└── static/
    ├── css/
    │   └── style.css     # Stylesheet
    └── js/
        └── script.js     # JavaScript logic
```

## Kalibrasi Sensor

Edit file `arduino_sketch.ino` dan sesuaikan nilai-nilai konversi:

```cpp
float waterHeight = (waterHeightRaw / 1023.0) * 100;    // Ubah 100 ke maksimal cm
float rainfall = (rainfallRaw / 1023.0) * 200;         // Ubah 200 ke maksimal mm
float windSpeed = (windSpeedRaw / 1023.0) * 100;       // Ubah 100 ke maksimal km/h
```

## Troubleshooting

### Database Error
Hapus file `flood_data.db` dan jalankan ulang:
```bash
rm flood_data.db
python app.py
```

### Arduino Connection Error
- Cek port COM di Device Manager (Windows)
- Update port di `arduino_client.py`:
```python
ARDUINO_PORT = 'COM3'  # Sesuaikan dengan port gess
```

### Data tidak muncul
- Pastikan Arduino terhubung dan sketch sudah ter-upload
- Cek Serial Monitor di Arduino IDE untuk debug
- Pastikan baud rate sama (9600)

## Pengembangan Lebih Lanjut

Fitur yang bisa ditambahkan jika ingin diseriusin:
- [ ] Integrasi SMS/Email untuk alert
- [ ] Dashboard dengan multiple stations
- [ ] Predictive modeling dengan ML
- [ ] Mobile app
- [ ] Data retention policy
- [ ] User authentication
- [ ] Data backup otomatis

**Catatan Penting:**
Sistem ini untuk coba coba dan monitoring lokal. Jika sistem mau diseriusin, pertimbangkan:
- Backup data otomatis
- Redundancy sensor
- Sistem alert multi-channel
- Testing & validation menyeluruh

**YA GITU LAH POKOKNYA**
