# ==============================================================================
# FILE TOOL: pin_tester.py
# Deskripsi: Tool Diagnostik & Detektor GPIO Tombol MacroPad untuk Thonny IDE.
#            Jalankan script ini (F5 di Thonny), lalu tekan tombol fisik untuk
#            melihat nomor GPIO dan nama variabel bitmask-nya (B0 - B9).
# ==============================================================================
import time
from machine import Pin

# 1. Coba ambil daftar pin dari config.py jika ada, jika tidak gunakan default
try:
    import config
    PINS = list(config.BUTTON_PINS)
    LED_PIN = getattr(config, "STATUS_LED_PIN", 8)
    print("[Info] Menggunakan daftar BUTTON_PINS dari config.py")
except Exception:
    PINS = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10]
    LED_PIN = 8
    print("[Info] Menggunakan daftar pin default:", PINS)

# 2. Inisialisasi seluruh pin tombol dengan internal PULL_UP (Active LOW)
buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in PINS]

# Inisialisasi LED indikator on-board (GPIO 8 Active LOW pada Super Mini)
led = None
if LED_PIN is not None and LED_PIN not in PINS:
    try:
        led = Pin(LED_PIN, Pin.OUT, value=1)  # 1 = Mati
    except Exception:
        led = None

def set_led(on):
    if led is not None:
        led.value(0 if on else 1)

def get_pressed_indices():
    """Mengembalikan list index tombol yang sedang tertekan (bernilai LOW/0)."""
    pressed = []
    for idx, btn in enumerate(buttons):
        if btn.value() == 0:
            pressed.append(idx)
    return pressed

def print_header():
    print("\n" + "=" * 62)
    print("   ESP32-C3 MACROPAD GPIO DETECTOR & BUTTON TESTER")
    print("=" * 62)
    print("Daftar Mapping Index Variabel -> Nomor GPIO:")
    for idx, pin_num in enumerate(PINS):
        print(f"  - B{idx:<2} (Bitmask 1 << {idx:<2} = {1 << idx:<4})  -->  GPIO {pin_num}")
    print("-" * 62)

    # Cek apakah ada pin yang langsung terhubung ke GND saat start
    stuck = get_pressed_indices()
    if stuck:
        stuck_info = ", ".join([f"GPIO {PINS[i]} (B{i})" for i in stuck])
        print(f"[PERINGATAN] Pin berikut terdeteksi LOW saat start: {stuck_info}")
        print("             Periksa apakah tombol tertekan atau kabel korslet ke GND!")
    else:
        print("[OK] Semua jalur GPIO berstatus normal (HIGH / Idle).")

    print("-" * 62)
    print("Silakan tekan 1 tombol atau beberapa tombol bersamaan...")
    print("(Tekan Ctrl+C atau tombol STOP di Thonny untuk keluar)\n")

def run_detector():
    print_header()
    prev_pressed = []

    try:
        while True:
            current_pressed = get_pressed_indices()

            # Jika ada perubahan status tombol
            if current_pressed != prev_pressed:
                # Beri jeda 25ms untuk debounce sekaligus menangkap penekanan combo
                time.sleep_ms(25)
                current_pressed = get_pressed_indices()

                if current_pressed != prev_pressed:
                    if current_pressed:
                        set_led(True)
                        # Format informasi GPIO dan Variabel B0..B9
                        gpio_list = [f"GPIO {PINS[i]}" for i in current_pressed]
                        var_list  = [f"B{i}" for i in current_pressed]
                        bitmask   = sum(1 << i for i in current_pressed)

                        if len(current_pressed) == 1:
                            idx = current_pressed[0]
                            print(
                                f"[DITEKAN] Tombol Tunggal : GPIO {PINS[idx]:<2}  | "
                                f"Variabel config.py: B{idx:<2}  | "
                                f"Bitmask: {bitmask} (0x{bitmask:03X})"
                            )
                        else:
                            gpio_str = " + ".join(gpio_list)
                            combo_str = "(" + " | ".join(var_list) + ")"
                            print(
                                f"[COMBO]   {len(current_pressed)} Tombol       : {gpio_str}  | "
                                f"Kode config.py: {combo_str}  | "
                                f"Bitmask: {bitmask} (0x{bitmask:03X})"
                            )
                    else:
                        set_led(False)
                        print("   └─> [DILEPAS] Semua tombol kembali idle.\n")

                    prev_pressed = current_pressed

            time.sleep_ms(10)

    except KeyboardInterrupt:
        set_led(False)
        print("\n[Selesai] Tool detektor GPIO dihentikan.")

if __name__ == "__main__":
    run_detector()