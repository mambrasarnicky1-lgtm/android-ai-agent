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
android.permissions = INTERNET, WAKE_LOCK, FOREGROUND_SERVICE, FOREGROUND_SERVICE_SPECIAL_USE, POST_NOTIFICATIONS, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, CAMERA, RECORD_AUDIO
android.gradle_dependencies =
android.api = 34
android.minapi = 26
services = NoirService:service.py
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.private_storage = True
android.enable_androidx = True
android.skip_update = False
android.accept_sdk_license = True
android.release_artifact = apk
android.gradle_args = --stacktrace --info -Dorg.gradle.jvmargs=-Xmx4096m
android.meta_data = moe.shizuku.client.V3_SUPPORT=true

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin