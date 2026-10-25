# ==============================================================================
# FILE 1: hid_keycodes.py
# Deskripsi: Daftar lengkap USB HID Keycodes untuk Keyboard TKL (Tenkeyless),
#            kombinasi Modifier, Descriptor BLE HID, dan konversi karakter ASCII.
# ==============================================================================
from micropython import const

# ------------------------------------------------------------------------------
# 1. BLE HID GATT UUIDs & REPORT DESCRIPTOR
# ------------------------------------------------------------------------------
UUID_SERVICE_HID         = const(0x1812)
UUID_CHAR_HID_INFO       = const(0x2A4A)
UUID_CHAR_REPORT_MAP     = const(0x2A4B)
UUID_CHAR_HID_CONTROL    = const(0x2A4C)
UUID_CHAR_REPORT         = const(0x2A4D)
UUID_CHAR_PROTOCOL_MODE  = const(0x2A4E)
UUID_DESC_REPORT_REF     = const(0x2908)

# Standard 8-Byte Keyboard Report Descriptor (Mendukung Keycode 0x00 s/d 0x73 / F24)
KEYBOARD_REPORT_DESC = bytes([
    0x05, 0x01,  # Usage Page (Generic Desktop)
    0x09, 0x06,  # Usage (Keyboard)
    0xA1, 0x01,  # Collection (Application)
    0x05, 0x07,  #   Usage Page (Key Codes)
    0x19, 0xE0,  #   Usage Minimum (224 - Left Control)
    0x29, 0xE7,  #   Usage Maximum (231 - Right GUI)
    0x15, 0x00,  #   Logical Minimum (0)
    0x25, 0x01,  #   Logical Maximum (1)
    0x75, 0x01,  #   Report Size (1)
    0x95, 0x08,  #   Report Count (8) - Modifier byte
    0x81, 0x02,  #   Input (Data, Variable, Absolute)
    0x95, 0x01,  #   Report Count (1)
    0x75, 0x08,  #   Report Size (8)
    0x81, 0x01,  #   Input (Constant) - Reserved byte
    0x95, 0x06,  #   Report Count (6) - 6-Key Rollover
    0x75, 0x08,  #   Report Size (8)
    0x15, 0x00,  #   Logical Minimum (0)
    0x25, 0x73,  #   Logical Maximum (115 / 0x73 - Mencakup seluruh TKL + F13-F24)
    0x05, 0x07,  #   Usage Page (Key Codes)
    0x19, 0x00,  #   Usage Minimum (0)
    0x29, 0x73,  #   Usage Maximum (115 / 0x73)
    0x81, 0x00,  #   Input (Data, Array)
    0xC0         # End Collection
])

# ------------------------------------------------------------------------------
# 2. MODIFIER KEYS (Byte ke-0 pada Report 8-Byte)
# ------------------------------------------------------------------------------
MOD_NONE        = const(0x00)
MOD_LEFT_CTRL   = const(0x01)
MOD_LEFT_SHIFT  = const(0x02)
MOD_LEFT_ALT    = const(0x04)
MOD_LEFT_GUI    = const(0x08)  # Tombol Windows / Command (Mac) / Super (Linux)
MOD_RIGHT_CTRL  = const(0x10)
MOD_RIGHT_SHIFT = const(0x20)
MOD_RIGHT_ALT   = const(0x40)  # AltGr
MOD_RIGHT_GUI   = const(0x80)

# Alias Singkat
MOD_CTRL  = MOD_LEFT_CTRL
MOD_SHIFT = MOD_LEFT_SHIFT
MOD_ALT   = MOD_LEFT_ALT
MOD_GUI   = MOD_LEFT_GUI
MOD_WIN   = MOD_LEFT_GUI
MOD_CMD   = MOD_LEFT_GUI

# Kombinasi Modifier Siap Pakai
MOD_CTRL_SHIFT      = const(MOD_LEFT_CTRL | MOD_LEFT_SHIFT)
MOD_CTRL_ALT        = const(MOD_LEFT_CTRL | MOD_LEFT_ALT)
MOD_CTRL_GUI        = const(MOD_LEFT_CTRL | MOD_LEFT_GUI)
MOD_SHIFT_ALT       = const(MOD_LEFT_SHIFT | MOD_LEFT_ALT)
MOD_SHIFT_GUI       = const(MOD_LEFT_SHIFT | MOD_LEFT_GUI)
MOD_ALT_GUI         = const(MOD_LEFT_ALT | MOD_LEFT_GUI)
MOD_CTRL_SHIFT_ALT  = const(MOD_LEFT_CTRL | MOD_LEFT_SHIFT | MOD_LEFT_ALT)
MOD_CTRL_SHIFT_GUI  = const(MOD_LEFT_CTRL | MOD_LEFT_SHIFT | MOD_LEFT_GUI)
MOD_CTRL_ALT_GUI    = const(MOD_LEFT_CTRL | MOD_LEFT_ALT | MOD_LEFT_GUI)

# ------------------------------------------------------------------------------
# 3. ALPHABET KEYS (A - Z)
# ------------------------------------------------------------------------------
KEY_NONE = const(0x00)
KEY_A    = const(0x04)
KEY_B    = const(0x05)
KEY_C    = const(0x06)
KEY_D    = const(0x07)
KEY_E    = const(0x08)
KEY_F    = const(0x09)
KEY_G    = const(0x0A)
KEY_H    = const(0x0B)
KEY_I    = const(0x0C)
KEY_J    = const(0x0D)
KEY_K    = const(0x0E)
KEY_L    = const(0x0F)
KEY_M    = const(0x10)
KEY_N    = const(0x11)
KEY_O    = const(0x12)
KEY_P    = const(0x13)
KEY_Q    = const(0x14)
KEY_R    = const(0x15)
KEY_S    = const(0x16)
KEY_T    = const(0x17)
KEY_U    = const(0x18)
KEY_V    = const(0x19)
KEY_W    = const(0x1A)
KEY_X    = const(0x1B)
KEY_Y    = const(0x1C)
KEY_Z    = const(0x1D)

# ------------------------------------------------------------------------------
# 4. NUMBER ROW KEYS (Angka Baris Atas 1 - 0)
# ------------------------------------------------------------------------------
KEY_1 = const(0x1E)  # 1 / !
KEY_2 = const(0x1F)  # 2 / @
KEY_3 = const(0x20)  # 3 / #
KEY_4 = const(0x21)  # 4 / $
KEY_5 = const(0x22)  # 5 / %
KEY_6 = const(0x23)  # 6 / ^
KEY_7 = const(0x24)  # 7 / &
KEY_8 = const(0x25)  # 8 / *
KEY_9 = const(0x26)  # 9 / (
KEY_0 = const(0x27)  # 0 / )

# ------------------------------------------------------------------------------
# 5. EDITING, WHITESPACE & PUNCTUATION (Area Utama TKL)
# ------------------------------------------------------------------------------
KEY_ENTER         = const(0x28)
KEY_ESC           = const(0x29)
KEY_ESCAPE        = KEY_ESC
KEY_BACKSPACE     = const(0x2A)
KEY_TAB           = const(0x2B)
KEY_SPACE         = const(0x2C)
KEY_MINUS         = const(0x2D)  # - / _
KEY_EQUAL         = const(0x2E)  # = / +
KEY_LEFT_BRACKET  = const(0x2F)  # [ / {
KEY_RIGHT_BRACKET = const(0x30)  # ] / }
KEY_BACKSLASH     = const(0x31)  # \ / |
KEY_NON_US_HASH   = const(0x32)  # # / ~ (ISO Layout)
KEY_SEMICOLON     = const(0x33)  # ; / :
KEY_APOSTROPHE    = const(0x34)  # ' / "
KEY_QUOTE         = KEY_APOSTROPHE
KEY_GRAVE         = const(0x35)  # ` / ~
KEY_TILDE         = KEY_GRAVE
KEY_COMMA         = const(0x36)  # , / <
KEY_DOT           = const(0x37)  # . / >
KEY_PERIOD        = KEY_DOT
KEY_SLASH         = const(0x38)  # / / ?
KEY_CAPS_LOCK     = const(0x39)

# ------------------------------------------------------------------------------
# 6. FUNCTION KEYS (F1 - F12 Standar TKL + F13 - F24 Ekstra Macro)
# ------------------------------------------------------------------------------
KEY_F1  = const(0x3A)
KEY_F2  = const(0x3B)
KEY_F3  = const(0x3C)
KEY_F4  = const(0x3D)
KEY_F5  = const(0x3E)
KEY_F6  = const(0x3F)
KEY_F7  = const(0x40)
KEY_F8  = const(0x41)
KEY_F9  = const(0x42)
KEY_F10 = const(0x43)
KEY_F11 = const(0x44)
KEY_F12 = const(0x45)

KEY_F13 = const(0x68)
KEY_F14 = const(0x69)
KEY_F15 = const(0x6A)
KEY_F16 = const(0x6B)
KEY_F17 = const(0x6C)
KEY_F18 = const(0x6D)
KEY_F19 = const(0x6E)
KEY_F20 = const(0x6F)
KEY_F21 = const(0x70)
KEY_F22 = const(0x71)
KEY_F23 = const(0x72)
KEY_F24 = const(0x73)

# ------------------------------------------------------------------------------
# 7. SYSTEM & NAVIGATION KEYS (Kluster Kanan TKL)
# ------------------------------------------------------------------------------
KEY_PRINT_SCREEN = const(0x46)
KEY_PRTSC        = KEY_PRINT_SCREEN
KEY_SCROLL_LOCK  = const(0x47)
KEY_PAUSE        = const(0x48)
KEY_BREAK        = KEY_PAUSE

KEY_INSERT       = const(0x49)
KEY_INS          = KEY_INSERT
KEY_HOME         = const(0x4A)
KEY_PAGE_UP      = const(0x4B)
KEY_PGUP         = KEY_PAGE_UP
KEY_DELETE       = const(0x4C)
KEY_DEL          = KEY_DELETE
KEY_END          = const(0x4D)
KEY_PAGE_DOWN    = const(0x4E)
KEY_PGDN         = KEY_PAGE_DOWN

# ------------------------------------------------------------------------------
# 8. ARROW KEYS & CONTEXT MENU (Bagian Bawah Kluster Kanan TKL)
# ------------------------------------------------------------------------------
KEY_RIGHT_ARROW  = const(0x4F)
KEY_LEFT_ARROW   = const(0x50)
KEY_DOWN_ARROW   = const(0x51)
KEY_UP_ARROW     = const(0x52)

KEY_RIGHT        = KEY_RIGHT_ARROW
KEY_LEFT         = KEY_LEFT_ARROW
KEY_DOWN         = KEY_DOWN_ARROW
KEY_UP           = KEY_UP_ARROW

KEY_APPLICATION  = const(0x65)  # Tombol Menu / Context Klik Kanan
KEY_MENU         = KEY_APPLICATION

# ------------------------------------------------------------------------------
# 9. HELPER KONVERSI TEKS ASCII KE HID (Untuk Macro Ketik String Otomatis)
# ------------------------------------------------------------------------------
_ASCII_MAP = {
    ' ': (MOD_NONE, KEY_SPACE),
    '\n': (MOD_NONE, KEY_ENTER),
    '\t': (MOD_NONE, KEY_TAB),
    '-': (MOD_NONE, KEY_MINUS),         '_': (MOD_SHIFT, KEY_MINUS),
    '=': (MOD_NONE, KEY_EQUAL),         '+': (MOD_SHIFT, KEY_EQUAL),
    '[': (MOD_NONE, KEY_LEFT_BRACKET),  '{': (MOD_SHIFT, KEY_LEFT_BRACKET),
    ']': (MOD_NONE, KEY_RIGHT_BRACKET), '}': (MOD_SHIFT, KEY_RIGHT_BRACKET),
    '\\': (MOD_NONE, KEY_BACKSLASH),    '|': (MOD_SHIFT, KEY_BACKSLASH),
    ';': (MOD_NONE, KEY_SEMICOLON),     ':': (MOD_SHIFT, KEY_SEMICOLON),
    "'": (MOD_NONE, KEY_APOSTROPHE),    '"': (MOD_SHIFT, KEY_APOSTROPHE),
    '`': (MOD_NONE, KEY_GRAVE),         '~': (MOD_SHIFT, KEY_GRAVE),
    ',': (MOD_NONE, KEY_COMMA),         '<': (MOD_SHIFT, KEY_COMMA),
    '.': (MOD_NONE, KEY_DOT),           '>': (MOD_SHIFT, KEY_DOT),
    '/': (MOD_NONE, KEY_SLASH),         '?': (MOD_SHIFT, KEY_SLASH),
    '!': (MOD_SHIFT, KEY_1),
    '@': (MOD_SHIFT, KEY_2),
    '#': (MOD_SHIFT, KEY_3),
    '$': (MOD_SHIFT, KEY_4),
    '%': (MOD_SHIFT, KEY_5),
    '^': (MOD_SHIFT, KEY_6),
    '&': (MOD_SHIFT, KEY_7),
    '*': (MOD_SHIFT, KEY_8),
    '(': (MOD_SHIFT, KEY_9),
    ')': (MOD_SHIFT, KEY_0),
}

def char_to_hid(char):
    """Konversi 1 karakter ASCII menjadi tuple (modifier, keycode)."""
    if 'a' <= char <= 'z':
        return (MOD_NONE, KEY_A + (ord(char) - ord('a')))
    if 'A' <= char <= 'Z':
        return (MOD_SHIFT, KEY_A + (ord(char) - ord('A')))
    if '1' <= char <= '9':
        return (MOD_NONE, KEY_1 + (ord(char) - ord('1')))
    if char == '0':
        return (MOD_NONE, KEY_0)
    return _ASCII_MAP.get(char, (MOD_NONE, KEY_NONE))