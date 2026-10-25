# ==============================================================================
# FILE 2: config.py
# Deskripsi: Konfigurasi Pin GPIO, Parameter Timing, dan Multi-Profile Keymap
#            untuk ESP32-C3 Super Mini MacroPad (10 Tombol).
# ==============================================================================
from hid_keycodes import *

# ------------------------------------------------------------------------------
# 1. IDENTITAS BLE & HARDWARE PIN
# ------------------------------------------------------------------------------
BLE_DEVICE_NAME = "C3-MacroPad"

# Daftar 10 GPIO sesuai urutan tombol (GPIO 0, 1, 2, 3, 4, 5, 6, 7, 9, 10)
# PENTING: Jangan menekan/menahan tombol pada GPIO 2 atau GPIO 9 saat pertama
# kali mencolokkan kabel USB agar board tidak tertahan di mode Bootloader.
#BUTTON_PINS = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10]
BUTTON_PINS = [9, 7, 10,  4, 5, 6,  2, 0, 1, 3]

# Pin LED On-board ESP32-C3 Super Mini (GPIO 8, Active LOW) untuk indikator profile
STATUS_LED_PIN = 8

# Parameter Timing (dalam milidetik)
CHORD_WINDOW_MS = 35    # Jeda waktu untuk mendeteksi penekanan 2+ tombol bersamaan
DEBOUNCE_MS     = 45    # Jeda anti-bouncing setelah tombol dilepas
KEY_HOLD_MS     = 20    # Durasi tahan keycode saat dikirim via BLE

# ------------------------------------------------------------------------------
# 2. DEFINISI BITMASK TOMBOL (B0 s/d B9)
# ------------------------------------------------------------------------------
B0 = 1 << 0   # Tombol 1  -> GPIO 0
B1 = 1 << 1   # Tombol 2  -> GPIO 1
B2 = 1 << 2   # Tombol 3  -> GPIO 2 (Strapping Pin)
B3 = 1 << 3   # Tombol 4  -> GPIO 3
B4 = 1 << 4   # Tombol 5  -> GPIO 4
B5 = 1 << 5   # Tombol 6  -> GPIO 5
B6 = 1 << 6   # Tombol 7  -> GPIO 6
B7 = 1 << 7   # Tombol 8  -> GPIO 7
B8 = 1 << 8   # Tombol 9  -> GPIO 9 (Strapping / Boot Pin)
B9 = 1 << 9   # Tombol 10 -> GPIO 10

# Perintah Khusus Ganti Profile
ACTION_NEXT_PROFILE = "NEXT_PROFILE"

# ------------------------------------------------------------------------------
# 3. KONFIGURASI MULTI-PROFILE MAPPING
# ------------------------------------------------------------------------------
# Format nilai (action) yang didukung pada setiap profile:
#   a) Tuple (MODIFIER, KEYCODE, ...)      -> Tekan shortcut (maks 6 keycode sekaligus)
#   b) List  [(MOD, KEY), (MOD, KEY), ...] -> Macro berurutan (sequence)
#   c) String "teks..."                    -> Ketik teks otomatis (akhiri \n untuk Enter)
#   d) ACTION_NEXT_PROFILE                 -> Pindah ke profile berikutnya
#   e) "PROFILE:NAMA_PROFILE"              -> Pindah langsung ke profile tertentu

PROFILE_ORDER = ["GENERAL", "CODING", "MEETING"]
DEFAULT_PROFILE = "GENERAL"

PROFILES = {
    # ==========================================================================
    # PROFILE 1: GENERAL / PRODUCTIVITY (Kedip LED 1x)
    # ==========================================================================
    "GENERAL": {
        # --- Single Button Press ---
        B0: (MOD_CTRL, KEY_C),                  # Copy
        B1: (MOD_CTRL, KEY_V),                  # Paste
        B2: (MOD_CTRL, KEY_X),                  # Cut
        B3: (MOD_CTRL, KEY_Z),                  # Undo
        B4: (MOD_CTRL, KEY_Y),                  # Redo
        B5: (MOD_CTRL, KEY_A),                  # Select All
        B6: (MOD_ALT, KEY_TAB),                 # Switch App (Alt + Tab)
        B7: (MOD_WIN | MOD_SHIFT, KEY_S),       # Screenshot Area (Win + Shift + S)
        B8: (MOD_WIN, KEY_L),                   # Lock PC (Win + L)
        B9: (MOD_NONE, KEY_ENTER),              # Enter

        # --- Combo / Chord Press (Tekan Bersamaan) ---
        (B0 | B1): (MOD_CTRL_SHIFT, KEY_V),     # Paste Without Formatting
        (B2 | B3): (MOD_CTRL_SHIFT, KEY_T),     # Reopen Closed Browser Tab
        (B6 | B7): (MOD_CTRL_GUI, KEY_RIGHT),   # Pindah Virtual Desktop Kanan
        (B8 | B9): ACTION_NEXT_PROFILE,         # Combo B8 + B9: Ganti ke Profile berikutnya
    },

    # ==========================================================================
    # PROFILE 2: CODING / TERMINAL / VS CODE (Kedip LED 2x)
    # ==========================================================================
    "CODING": {
        # --- Single Button Press ---
        B0: (MOD_CTRL, KEY_GRAVE),              # Toggle Terminal VS Code (Ctrl + `)
        B1: (MOD_CTRL_SHIFT, KEY_P),            # Command Palette (Ctrl + Shift + P)
        B2: (MOD_CTRL, KEY_SLASH),              # Toggle Line Comment (Ctrl + /)
        B3: (MOD_SHIFT_ALT, KEY_DOWN),          # Duplicate Line Down (Shift + Alt + Down)
        B4: (MOD_CTRL, KEY_D),                  # Select Next Occurrence (Ctrl + D)
        B5: (MOD_CTRL_SHIFT, KEY_K),            # Delete Line (Ctrl + Shift + K)
        B6: (MOD_CTRL, KEY_B),                  # Toggle Sidebar (Ctrl + B)
        B7: [(MOD_CTRL, KEY_K), (MOD_CTRL, KEY_S)], # Sequence: Buka Keyboard Shortcuts
        B8: "git status\n",                     # Auto-type command git status + Enter
        B9: (MOD_CTRL_ALT, KEY_T),              # Buka Terminal Linux (Ctrl + Alt + T)

        # --- Combo / Chord Press ---
        (B0 | B1): "git add . && git commit -m \"update\"\n",
        (B2 | B3): (MOD_SHIFT_ALT, KEY_F),      # Format Document (Shift + Alt + F)
        (B8 | B9): ACTION_NEXT_PROFILE,         # Combo B8 + B9: Ganti ke Profile berikutnya
    },

    # ==========================================================================
    # PROFILE 3: MEETING & STREAMING (Kedip LED 3x)
    # ==========================================================================
    "MEETING": {
        # --- Single Button Press ---
        B0: (MOD_CTRL, KEY_D),                  # Mute/Unmute Google Meet (Ctrl + D)
        B1: (MOD_CTRL, KEY_E),                  # Toggle Camera Google Meet (Ctrl + E)
        B2: (MOD_CTRL_ALT, KEY_H),              # Raise Hand Google Meet (Ctrl + Alt + H)
        B3: (MOD_ALT, KEY_A),                   # Mute/Unmute Zoom (Alt + A)
        B4: (MOD_ALT, KEY_V),                   # Toggle Video Zoom (Alt + V)
        B5: (MOD_CTRL_SHIFT, KEY_M),            # Mute/Unmute Discord/Teams (Ctrl + Shift + M)
        B6: (MOD_CTRL_SHIFT, KEY_D),            # Deafen Discord (Ctrl + Shift + D)
        B7: (MOD_NONE, KEY_F13),                # Custom Hotkey OBS Scene 1 (F13)
        B8: (MOD_NONE, KEY_F14),                # Custom Hotkey OBS Scene 2 (F14)
        B9: (MOD_NONE, KEY_ESC),                # Escape / Exit Fullscreen

        # --- Combo / Chord Press ---
        (B0 | B1): [(MOD_CTRL, KEY_D), (MOD_CTRL, KEY_E)], # Matikan Mic & Kamera sekaligus
        (B8 | B9): ACTION_NEXT_PROFILE,         # Combo B8 + B9: Kembali ke Profile 1
    },
}
