[app]
title = Noir SMC
package.name = noir_smc
package.domain = org.noir.agent
source.dir = mobile_app
source.include_exts = py,png,jpg,kv,atlas
version = 14.0.32
requirements = python3,kivy,requests,urllib3,certifi,idna,chardet,psutil,pillow
orientation = portrait
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, WAKE_LOCK, SYSTEM_ALERT_WINDOW
android.api = 33
android.minapi = 21
android.ndk = 25b
android.private_storage = True
services = NoirService:service.py
android.skip_update = False
android.accept_sdk_license = True
android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin