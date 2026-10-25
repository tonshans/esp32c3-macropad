# ==============================================================================
# FILE 3: main.py
# Deskripsi: Engine Utama BLE HID MacroPad untuk ESP32-C3 Super Mini.
#            Mendukung 10 GPIO, Chording/Combo, Multi-Profile, Macro Sequence,
#            Auto-Type String, dan Bonding/Security Permanen untuk Debian BlueZ.
# ==============================================================================
import asyncio
import aioble
import aioble.security as security
import bluetooth
from machine import Pin

import config
from hid_keycodes import (
    UUID_SERVICE_HID,
    UUID_CHAR_HID_INFO,
    UUID_CHAR_REPORT_MAP,
    UUID_CHAR_HID_CONTROL,
    UUID_CHAR_REPORT,
    UUID_CHAR_PROTOCOL_MODE,
    UUID_DESC_REPORT_REF,
    KEYBOARD_REPORT_DESC,
    char_to_hid,
)

# ------------------------------------------------------------------------------
# 1. INISIALISASI HARDWARE (10 TOMBOL & LED INDIKATOR)
# ------------------------------------------------------------------------------
buttons = [Pin(pin_num, Pin.IN, Pin.PULL_UP) for pin_num in config.BUTTON_PINS]

# Inisialisasi LED Indikator (GPIO 8 pada Super Mini adalah Active LOW: 1=Mati, 0=Nyala)
status_led = None
if getattr(config, "STATUS_LED_PIN", None) is not None:
    status_led = Pin(config.STATUS_LED_PIN, Pin.OUT, value=1)

# State Profile Aktif
current_profile_name = config.DEFAULT_PROFILE
if current_profile_name not in config.PROFILES:
    current_profile_name = config.PROFILE_ORDER[0]

# ------------------------------------------------------------------------------
# 2. REGISTRASI LAYANAN BLE HID (HOGP STANDAR)
# ------------------------------------------------------------------------------
EMPTY_REPORT = b"\x00" * 8

hid_service = aioble.Service(bluetooth.UUID(UUID_SERVICE_HID))

# Characteristic utama untuk pengiriman report tombol (Input Report)
# PENTING: initial=EMPTY_REPORT wajib ada agar Debian BlueZ (hog-lib.c) tidak
# gagal saat melakukan report_read_cb() pada awal koneksi.
report_char = aioble.Characteristic(
    hid_service,
    bluetooth.UUID(UUID_CHAR_REPORT),
    read=True,
    write=True,
    notify=True,
    initial=EMPTY_REPORT,
)

# Report Reference Descriptor (Report ID = 0, Report Type = 1 [Input])
aioble.Descriptor(
    report_char,
    bluetooth.UUID(UUID_DESC_REPORT_REF),
    read=True,
    initial=b"\x00\x01",
)

# Characteristic wajib standar HID Over GATT Profile (HOGP)
aioble.Characteristic(
    hid_service,
    bluetooth.UUID(UUID_CHAR_REPORT_MAP),
    read=True,
    initial=KEYBOARD_REPORT_DESC,
)
aioble.Characteristic(
    hid_service,
    bluetooth.UUID(UUID_CHAR_HID_INFO),
    read=True,
    initial=b"\x01\x01\x00\x02",
)
aioble.Characteristic(
    hid_service,
    bluetooth.UUID(UUID_CHAR_HID_CONTROL),
    write=True,
    write_no_response=True,
    initial=b"\x00",
)
aioble.Characteristic(
    hid_service,
    bluetooth.UUID(UUID_CHAR_PROTOCOL_MODE),
    read=True,
    write=True,
    write_no_response=True,
    initial=b"\x01",
)

# Register layanan GATT terlebih dahulu (otomatis mengaktifkan radio BLE)
aioble.register_services(hid_service)

# Konfigurasi parameter BLE dilakukan SETELAH register_services agar:
# 1. gap_name tidak ter-reset menjadi "mpy-esp32" oleh ble_svc_gap_init()
# 2. Fitur bonding (pertukaran & penyimpanan LTK/IRK) aktif di level stack NimBLE
ble = bluetooth.BLE()
for _param in (
    {"gap_name": config.BLE_DEVICE_NAME},
    {"bond": True},
    {"le_secure": True},
    {"mitm": False},
    {"io": 3},        # 3 = IO_CAPABILITY_NO_INPUT_OUTPUT ("Just Works")
    {"addr_mode": 0}, # 0 = Public Static MAC Address
):
    try:
        ble.config(**_param)
    except Exception:
        pass

connection = None

# ------------------------------------------------------------------------------
# 3. HELPER PENYIMPANAN KUNCI BONDING (FLASH JSON)
# ------------------------------------------------------------------------------
def load_ble_secrets():
    """Memuat kunci bonding LTK/IRK dari flash saat boot."""
    try:
        if hasattr(security, "load_secrets"):
            security.load_secrets()
        elif hasattr(security, "_load_secrets"):
            security._load_secrets()
    except Exception as err:
        print("[Security] Info load secrets:", err)

def save_ble_secrets():
    """Menyimpan kunci bonding LTK/IRK ke flash begitu pairing selesai."""
    try:
        if getattr(security, "_modified", False):
            if hasattr(security, "save_secrets"):
                security.save_secrets()
            elif hasattr(security, "_save_secrets"):
                security._save_secrets()
            security._modified = False
            print("[Security] Kunci bonding berhasil disimpan ke flash.")
    except Exception as err:
        print("[Security] Info save secrets:", err)

# ------------------------------------------------------------------------------
# 4. FUNGSI INDIKATOR LED & MANAJEMEN PROFILE
# ------------------------------------------------------------------------------
async def blink_led(times, interval_ms=120):
    """Mengedipkan LED on-board sebanyak `times` kali (Non-blocking)."""
    if status_led is None:
        return
    for _ in range(times):
        status_led.value(0)  # ON (Active LOW)
        await asyncio.sleep_ms(interval_ms)
        status_led.value(1)  # OFF
        await asyncio.sleep_ms(interval_ms)

async def switch_profile(target_name=None):
    """Mengganti profile aktif dan memberi feedback kedipan LED."""
    global current_profile_name
    order = config.PROFILE_ORDER

    if target_name and target_name in config.PROFILES:
        current_profile_name = target_name
    else:
        try:
            idx = order.index(current_profile_name)
            next_idx = (idx + 1) % len(order)
            current_profile_name = order[next_idx]
        except ValueError:
            current_profile_name = order[0]

    # Hitung nomor urut profile (1-based) untuk jumlah kedipan LED
    try:
        blink_count = order.index(current_profile_name) + 1
    except ValueError:
        blink_count = 1

    print("[Profile] Aktif:", current_profile_name)
    await blink_led(blink_count)

# ------------------------------------------------------------------------------
# 5. FUNGSI PENGIRIMAN REPORT BLE HID YANG AMAN (CRASH-SAFE)
# ------------------------------------------------------------------------------
def is_ble_ready():
    """Memastikan koneksi BLE masih aktif sebelum mengirim paket."""
    if connection is None:
        return False
    try:
        return connection.is_connected()
    except AttributeError:
        return True

async def send_key_tuple(key_tuple):
    """
    Mengirim 1 kombinasi shortcut HID.
    Mendukung format (modifier, key1) hingga (modifier, key1, key2, ..., key6).
    """
    if not is_ble_ready() or not key_tuple:
        return

    modifier = key_tuple[0] & 0xFF
    keys = list(key_tuple[1:7])
    while len(keys) < 6:
        keys.append(0x00)

    report = bytes([modifier, 0x00] + keys)
    try:
        report_char.notify(connection, report)
        await asyncio.sleep_ms(config.KEY_HOLD_MS)
        report_char.notify(connection, EMPTY_REPORT)
        await asyncio.sleep_ms(config.KEY_HOLD_MS)
    except Exception as err:
        print("[BLE Notify Error]:", err)

async def send_text_string(text):
    """Mengetik string ASCII karakter demi karakter secara otomatis."""
    for ch in text:
        if not is_ble_ready():
            break
        mod, code = char_to_hid(ch)
        if code != 0x00:
            await send_key_tuple((mod, code))

async def execute_action(action):
    """Mengeksekusi action dari kamus profile sesuai tipe datanya."""
    if action is None:
        return

    # 1. Perintah ganti profile atau ketik teks string
    if isinstance(action, str):
        if action == config.ACTION_NEXT_PROFILE:
            await switch_profile()
            return
        if action.startswith("PROFILE:"):
            target = action.split(":", 1)[1].strip()
            await switch_profile(target)
            return
        await send_text_string(action)
        return

    # 2. Tuple tunggal: (modifier, key1, [key2...])
    if isinstance(action, tuple):
        await send_key_tuple(action)
        return

    # 3. List sequence macro: [(mod1, key1), (mod2, key2), ...]
    if isinstance(action, list):
        for step in action:
            if isinstance(step, tuple):
                await send_key_tuple(step)
            elif isinstance(step, str):
                await send_text_string(step)
            elif isinstance(step, int):
                # Angka integer di dalam list berfungsi sebagai jeda delay (ms)
                await asyncio.sleep_ms(step)

# ------------------------------------------------------------------------------
# 6. SCANNER TOMBOL & CHORDING BITMASK
# ------------------------------------------------------------------------------
def read_button_bitmask(active_pins_mask):
    """Membaca seluruh pin tombol menjadi 1 integer bitmask (Active LOW)."""
    mask = 0
    for idx, btn in enumerate(buttons):
        if btn.value() == 0:
            mask |= (1 << idx)
    return mask & active_pins_mask

async def button_scanner():
    # Mask seluruh bit tombol yang valid (10 tombol -> 0x3FF)
    active_pins_mask = (1 << len(buttons)) - 1

    # Deteksi awal saat boot: proteksi jika ada tombol terjepit/korslet ke GND
    await asyncio.sleep_ms(50)
    initial_stuck = read_button_bitmask(active_pins_mask)
    if initial_stuck != 0:
        print("[Peringatan] Pin terdeteksi LOW saat boot:", bin(initial_stuck))
        for _ in range(40):
            await asyncio.sleep_ms(50)
            if read_button_bitmask(active_pins_mask) == 0:
                initial_stuck = 0
                break
        if initial_stuck != 0:
            print("[Proteksi] Mengisolasi pin yang stuck:", bin(initial_stuck))
            active_pins_mask &= ~initial_stuck

    prev_mask = 0
    sample_steps = max(1, config.CHORD_WINDOW_MS // 5)

    while True:
        current_mask = read_button_bitmask(active_pins_mask)

        # Transisi dari idle (0) -> ada tombol yang ditekan
        if current_mask != 0 and prev_mask == 0:
            # Multi-sampling selama CHORD_WINDOW_MS agar tap cepat maupun combo
            # dua tombol yang tidak presisi bersamaan tetap tertangkap akurat.
            accumulated_mask = current_mask
            for _ in range(sample_steps):
                await asyncio.sleep_ms(5)
                accumulated_mask |= read_button_bitmask(active_pins_mask)

            # Ambil keymap dari profile yang sedang aktif
            active_map = config.PROFILES.get(current_profile_name, {})
            action = active_map.get(accumulated_mask)

            if action is not None:
                await execute_action(action)

            # Tunggu sampai semua tombol dilepas (batas aman 5 detik anti-hang)
            wait_ms = 0
            while read_button_bitmask(active_pins_mask) != 0 and wait_ms < 5000:
                await asyncio.sleep_ms(15)
                wait_ms += 15

            prev_mask = 0
            await asyncio.sleep_ms(config.DEBOUNCE_MS)
            continue

        prev_mask = current_mask
        await asyncio.sleep_ms(10)

# ------------------------------------------------------------------------------
# 7. TASK ADVERTISING & KEAMANAN BONDING BLE
# ------------------------------------------------------------------------------
async def ble_advertising_task():
    global connection
    service_uuid = bluetooth.UUID(UUID_SERVICE_HID)

    while True:
        print("[BLE] Menunggu koneksi pada perangkat:", config.BLE_DEVICE_NAME)
        try:
            connection = await aioble.advertise(
                250_000,
                name=config.BLE_DEVICE_NAME,
                services=[service_uuid],
                appearance=0x03C1,  # Icon Keyboard HID Standar
            )
            print("[BLE] Terhubung ke perangkat host!")
            await blink_led(1, 200)

            # Pastikan buffer report bersih saat awal koneksi
            try:
                report_char.write(EMPTY_REPORT)
            except Exception:
                pass

            # Beri waktu 800ms bagi Debian BlueZ untuk menyelesaikan GATT / enkripsi
            await asyncio.sleep_ms(800)
            save_ble_secrets()

            # Jika link belum terenkripsi (misal saat reconnect), kirim SMP Security Request
            if is_ble_ready() and not getattr(connection, "encrypted", False) and hasattr(security, "pair"):
                try:
                    await security.pair(
                        connection,
                        bond=True,
                        le_secure=True,
                        mitm=False,
                        timeout_ms=10000,
                    )
                except Exception as pair_err:
                    print("[BLE Security Info]:", pair_err)
                save_ble_secrets()

            # Cek berkala selama 3 detik pertama untuk memastikan kunci bonding
            # dari BlueZ langsung tertulis ke file flash ble_secrets.json
            for _ in range(5):
                if not is_ble_ready():
                    break
                await asyncio.sleep_ms(600)
                save_ble_secrets()

            # Tunggu hingga host memutuskan koneksi (tanpa batas timeout)
            await connection.disconnected(timeout_ms=None)
            print("[BLE] Koneksi terputus.")
        except Exception as err:
            print("[BLE Error]:", err)
        finally:
            save_ble_secrets()
            connection = None
            await asyncio.sleep_ms(1500)

# ------------------------------------------------------------------------------
# 8. ENTRY POINT UTAMA
# ------------------------------------------------------------------------------
async def main():
    print("=== ESP32-C3 BLE MacroPad Dimulai ===")
    print("Profile Awal:", current_profile_name)
    load_ble_secrets()
    await blink_led(1, 150)
    await asyncio.gather(
        ble_advertising_task(),
        button_scanner(),
    )

if __name__ == "__main__":
    asyncio.run(main())
