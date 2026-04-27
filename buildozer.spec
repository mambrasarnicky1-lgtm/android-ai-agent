[app]
title = Noir Sovereign Elite v17.5
package.name = noir_sovereign
package.domain = org.noir.sovereign
source.dir = mobile_app
source.include_exts = py,png,jpg,kv,atlas
version = 17.5.7
requirements = python3,kivy,requests,pillow,pyjnius,cython,pycryptodome,urllib3,certifi,idna,chardet,adb-shell,cryptography,setuptools
p4a.branch = v2024.01.21
orientation = portrait
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, WAKE_LOCK, SYSTEM_ALERT_WINDOW, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE, BIND_ACCESSIBILITY_SERVICE, moe.shizuku.manager.permission.API_V23, PACKAGE_USAGE_STATS, QUERY_ALL_PACKAGES
android.gradle_dependencies =
android.api = 34
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
android.gradle_args = --stacktrace --info -Dorg.gradle.jvmargs=-Xmx4096m
android.meta_data = moe.shizuku.client.V3_SUPPORT=true

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin