[app]
title = Noir Sovereign V21.1 NATIVE
package.name = noir_sovereign
package.domain = org.noir.sovereign
source.dir = mobile_app
source.include_exts = py,png,jpg,kv,atlas,java
source.include_patterns = java/**/*, java/**/**/*
version = 21.1.0

requirements = python3,kivy,requests,pillow,pyjnius,cython,pycryptodomex,urllib3,certifi,idna,charset-normalizer,setuptools

p4a.branch = v2024.01.21
orientation = portrait

# ─── PERMISSIONS (Full Native Set) ───────────────────────────────────────────
android.permissions =
    INTERNET,
    WAKE_LOCK,
    FOREGROUND_SERVICE,
    FOREGROUND_SERVICE_MEDIA_PROJECTION,
    FOREGROUND_SERVICE_MICROPHONE,
    FOREGROUND_SERVICE_SPECIAL_USE,
    POST_NOTIFICATIONS,
    RECEIVE_BOOT_COMPLETED,
    RECORD_AUDIO,
    CAMERA,
    READ_MEDIA_IMAGES,
    READ_MEDIA_VIDEO,
    READ_MEDIA_AUDIO,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    ACCESS_FINE_LOCATION,
    ACCESS_COARSE_LOCATION,
    ACCESS_BACKGROUND_LOCATION

android.api = 34
android.minapi = 26
android.ndk = 25b
android.ndk_api = 26
android.archs = arm64-v8a
android.private_storage = True
android.enable_androidx = True
android.skip_update = False
android.accept_sdk_license = True
android.release_artifact = apk

# ─── NATIVE SERVICE DECLARATIONS via AndroidManifest entries ─────────────────
android.manifest.application_attributes = android:usesCleartextTraffic="true"
android.allow_backup = False

# Register Native Service, Boot Receiver, and Projection Activity
android.extra_manifest_xml =
    <service android:name="org.noir.sovereign.NoirNativeService"
             android:foregroundServiceType="mediaProjection|microphone"
             android:exported="false" />
    <receiver android:name="org.noir.sovereign.NoirBootReceiver"
              android:exported="false">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED" />
            <action android:name="android.intent.action.QUICKBOOT_POWERON" />
        </intent-filter>
    </receiver>
    <activity android:name="org.noir.sovereign.NoirProjectionActivity"
              android:theme="@android:style/Theme.Translucent.NoTitleBar"
              android:exported="false" />

android.gradle_dependencies = androidx.core:core:1.12.0

android.gradle_args = --stacktrace -Dorg.gradle.jvmargs=-Xmx4096m

# Java source directories to compile alongside p4a
android.java_dir = java

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin