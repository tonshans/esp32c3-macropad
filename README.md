# 💻 ESP32-C3 BLE MacroPad

C3-MacroPad adalah proyek DIY Bluetooth Low Energy (BLE) Macro Keyboard berbasis **ESP32-C3 Super Mini** dan **MicroPython**. Proyek ini dirancang khusus dengan fitur *Bonding Security* (Penyimpanan kunci LTK/IRK ke NVS Flash) dan penguncian Public MAC Address sehingga sangat stabil saat digunakan di lingkungan sistem operasi yang ketat seperti **Linux (Debian/BlueZ)**, Windows, maupun macOS.

## ✨ Fitur Utama
- **10 Tombol Hardware:** Mendukung single-press dan kombinasi/chord (beberapa tombol ditekan bersamaan).
- **Multi-Profile:** Pindah mode seketika (contoh: Mode General, Coding, Meeting) lengkap dengan indikator kedipan LED on-board.
- **Advanced Mapping:** Bisa memetakan tombol untuk shortcut standar, *sequence macro* berurutan, hingga mengetik teks (*auto-type*) secara instan.
- **Linux/Debian Optimized:** Memperbaiki masalah *reconnect loop* khas BlueZ berkat integrasi `aioble.security` (NVS Bonding) dan Public Address HOGP.
- **Bebas Komponen Ekstra:** Tidak butuh resistor eksternal karena menggunakan internal *pull-up*.

---

## 🛠️ Kebutuhan Hardware
* 1x Board **ESP32-C3 Super Mini**
* 10x Push Button Mekanik / Tactile Switch
* Kabel jumper secukupnya

### Skema Pinout & Wiring
Pasangkan satu kaki dari masing-masing tombol ke pin GPIO berikut, dan kaki pasangannya satukan semua ke **GND** (*Common Ground*).

| Tombol | Pin GPIO ESP32-C3 | Variabel | Catatan Khusus |
| :--- | :--- | :--- | :--- |
| Tombol 1 | GPIO 0 | `B0` | Aman |
| Tombol 2 | GPIO 1 | `B1` | Aman |
| Tombol 3 | GPIO 2 | `B2` | **Strapping Pin** (Jangan ditekan saat colok USB) |
| Tombol 4 | GPIO 3 | `B3` | Aman |
| Tombol 5 | GPIO 4 | `B4` | Aman |
| Tombol 6 | GPIO 5 | `B5` | Aman |
| Tombol 7 | GPIO 6 | `B6` | Aman |
| Tombol 8 | GPIO 7 | `B7` | Aman |
| Tombol 9 | GPIO 9 | `B8` | **Boot Pin** (Jangan ditekan saat colok USB) |
| Tombol 10| GPIO 10 | `B9` | Aman |

*(LED Indikator Profile menggunakan **GPIO 8** bawaan board Super Mini).*

---

## 🚀 Instalasi Software
1. Flash board ESP32-C3 Anda dengan **MicroPython** terbaru.
2. Install library `aioble` ke dalam board (bisa melalui *Tools -> Manage Packages* di Thonny IDE).
3. Salin 3 file utama dari *repository* ini ke direktori *root* (/) ESP32-C3 Anda:
   - `hid_keycodes.py` (Berisi kamus identifier tombol keyboard)
   - `config.py` (Tempat Anda mengubah pemetaan tombol/shortcut)
   - `main.py` (Engine utama BLE & Scanner tombol)
4. Opsional: Simpan `pin_tester.py` jika sewaktu-waktu Anda lupa urutan GPIO dan butuh *debugging* hardware.

---

## ⚙️ Konfigurasi (`config.py`)
Anda hanya perlu mengedit file `config.py` untuk menyesuaikan shortcut.
Setiap profile menerima beberapa format *Action*:
- **Tuple Kombinasi:** `(MOD_CTRL, KEY_C)` -> (Ctrl + C)
- **Teks Langsung:** `"git status\n"` -> Mengetik string otomatis dan Enter
- **Sequence Macro:** `[(MOD_CTRL, KEY_K), (MOD_CTRL, KEY_S)]` -> Shortcut berurutan
- **Ganti Profile:** `ACTION_NEXT_PROFILE`

Secara default, kombinasi **Tombol 9 + Tombol 10 (`B8 | B9`)** digunakan untuk berpindah profile.

---

## 🐧 Panduan Pairing Khusus Linux (Debian / BlueZ)
Jika Anda menggunakan Linux, lakukan *pairing* via `bluetoothctl` di terminal (bukan lewat GUI Manager) agar proses *bonding security* tersimpan dengan sempurna di *cache* OS:

```bash
# 1. Buka bluetoothctl
bluetoothctl

# 2. Nyalakan pemindaian
scan on
# (Tunggu sampai MAC Address 'C3-MacroPad' muncul, lalu matikan scan)
scan off

# 3. Trust, Pair, dan Connect
trust [MAC_ADDRESS_MACROPAD]
pair [MAC_ADDRESS_MACROPAD]
connect [MAC_ADDRESS_MACROPAD]
```

**⚠️ Troubleshooting Putus-Nyambung (Reconnect Loop) di Linux:**
Jika sebelumnya Anda pernah melakukan *pairing* namun *firmware* error dan sekarang C3-Macropad tidak mau tersambung ulang:
1. Cabut USB Macropad.
2. Bersihkan *cache* Bluetooth yang nyangkut di Debian:
   ```bash
   sudo rm -rf /var/lib/bluetooth/[MAC_LAPTOP]/[MAC_MACROPAD]
   sudo systemctl restart bluetooth
   ```
3. Colok kembali Macropad dan lakukan proses *pairing* `bluetoothctl` dari awal. Setelah pesan `[Security] Kunci bonding berhasil disimpan ke flash` muncul di Thonny, koneksi akan menjadi permanen dan stabil.

---

## 🧩 Menggunakan Tool Diagnostik (`pin_tester.py`)
Jika Anda merakit ulang kabel dan bingung tombol mana terhubung ke pin mana:
1. Hentikan (Stop) `main.py` di Thonny.
2. Buka `pin_tester.py` dan klik **Run**.
3. Tekan sembarang tombol di MacroPad Anda, dan layar Thonny akan menampilkan informasi Pin GPIO, Variabel (`B0`-`B9`), dan Bitmask yang sedang ditekan. 