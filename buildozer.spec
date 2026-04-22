[app]

# (str) Title of your application
title = Noir SMC

# (str) Package name
package.name = noir_smc

# (str) Package domain (needed for android packaging)
package.domain = org.noir.agent

# (str) Source code where the main.py live
source.dir = mobile_app

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 14.0.50

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,idna,chardet,pillow,pyjnius,jpeg,png,openssl

# (str) p4a branch to use
p4a.branch = master

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, WAKE_LOCK, SYSTEM_ALERT_WINDOW

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android architectures to build for
android.archs = arm64-v8a

# (bool) use posix to build the android app
android.private_storage = True

# (bool) enable AndroidX
android.enable_androidx = True

# (list) List of service to declare
services = NoirService:service.py

# (bool) skip check of the sdk/ndk
android.skip_update = False

# (bool) accept the sdk license
android.accept_sdk_license = True

# (str) The format used to package the app for release mode (apk or aab)
android.release_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build directory (the place where the build is performed)
build_dir = ./.buildozer

# (str) Path to bin directory (the place where the finished objects are stored)
bin_dir = ./bin