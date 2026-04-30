[app]
title = Noir Sovereign V21.0 AEGIS
package.name = noir_sovereign
package.domain = org.noir.sovereign
source.dir = mobile_app
source.include_exts = py,png,jpg,kv,atlas
version = 21.0.0
requirements = python3,kivy,requests,pillow,pyjnius,cython,pycryptodomex,urllib3,certifi,idna,charset-normalizer,adb-shell,setuptools
p4a.branch = v2024.01.21
orientation = portrait
android.permissions = INTERNET, WAKE_LOCK, FOREGROUND_SERVICE, FOREGROUND_SERVICE_SPECIAL_USE, POST_NOTIFICATIONS, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, CAMERA, RECORD_AUDIO, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, moe.shizuku.manager.permission.API_V23
android.gradle_dependencies =
android.api = 34
android.minapi = 26
services = NoirService:service.py
android.ndk = 25b
android.ndk_api = 26
android.archs = arm64-v8a
android.private_storage = True
android.enable_androidx = True
android.skip_update = False
android.accept_sdk_license = True
android.release_artifact = apk
android.gradle_args = --stacktrace --info -Dorg.gradle.jvmargs=-Xmx4096m
android.meta_data = moe.shizuku.client.V3_SUPPORT=true

# --- HYPEROS & RELEASE STABILITY FIXES ---
# Wajib untuk mem-bypass blokir Android 14 terhadap URL HTTP (Direct-VPS)
android.manifest.application_attributes = android:usesCleartextTraffic="true"
android.allow_backup = False

# Auto-Sign configuration (Jika menggunakan environment variables nanti)
# P4A_RELEASE_KEYSTORE, P4A_RELEASE_KEYALIAS, P4A_RELEASE_KEYSTORE_PASSWD

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin