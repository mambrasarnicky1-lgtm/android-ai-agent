[app]

# --- Identitas Aplikasi ---
title = Noir Sovereign v14
package.name = noirsmc
package.domain = org.antigravity
version = 14.0.35

# --- Sumber Kode ---
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.exclude_dirs = tests, bin, .buildozer

# --- Requirements ---
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,chardet,pillow,pyjnius,jpeg,png

# --- Target Platform ---
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.skip_update = False

# --- Arsitektur (arm64-v8a target utama Redmi Note 14) ---
android.archs = arm64-v8a

# --- Izin Sistem ---
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK,FOREGROUND_SERVICE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,CAMERA,RECEIVE_BOOT_COMPLETED,SYSTEM_ALERT_WINDOW,VIBRATE,POST_NOTIFICATIONS,moe.shizuku.manager.permission.API_V23

# --- Orientasi ---
orientation = portrait
fullscreen = 0

# --- Branch p4a ---
p4a.branch = master

# --- Gradle ---
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
