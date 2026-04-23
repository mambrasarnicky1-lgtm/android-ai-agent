[app]
title = Noir Sovereign ELITE v16.0.03
package.name = noirelitev16
package.domain = org.noir.elite
source.dir = mobile_app
source.include_exts = py,png,jpg,kv,atlas
version = 16.0.03
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,chardet,pillow,pyjnius,jpeg,png,openssl,pycryptodome
p4a.branch = master
orientation = portrait
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, WAKE_LOCK, SYSTEM_ALERT_WINDOW, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE, BIND_ACCESSIBILITY_SERVICE
android.gradle_dependencies = 
android.api = 33
android.minapi = 21
services = NoirService:service.py
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.private_storage = True
android.enable_androidx = True
android.skip_update = False
android.accept_sdk_license = True
android.release_artifact = apk
android.gradle_args = --stacktrace --info -Dorg.gradle.jvmargs=-Xmx2048m

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin