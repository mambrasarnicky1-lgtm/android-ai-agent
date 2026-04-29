import subprocess

ADB_PATH = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd_suffix):
    cmd = f'"{ADB_PATH}" {cmd_suffix}'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip()

print("=== NOIR SOVEREIGN: V20.1 LIVE AUDIT ===")

# 1. Device Check
out, err = run_adb("devices")
print(out)

# 2. Check Installed APK Version
print("\n--- INSTALLED APK VERSION ---")
out, err = run_adb('shell dumpsys package org.noir.sovereign.noir_sovereign | grep versionName')
if out:
    print(out)
else:
    print("Package not found or grep failed. Trying alternate method...")
    out2, err2 = run_adb('shell dumpsys package org.noir.sovereign.noir_sovereign')
    for line in out2.split('\n'):
        if "versionName" in line or "versionCode" in line:
            print(line.strip())

# 3. Check if Process is Running
print("\n--- PROCESS STATUS ---")
out, err = run_adb('shell "pidof org.noir.sovereign.noir_sovereign"')
if out:
    print(f"STATUS: RUNNING (PID: {out})")
else:
    print("STATUS: NOT RUNNING. Attempting to force launch...")
    # Launch if not running
    run_adb('shell monkey -p org.noir.sovereign.noir_sovereign -c android.intent.category.LAUNCHER 1')
    import time
    time.sleep(3)
    out, err = run_adb('shell "pidof org.noir.sovereign.noir_sovereign"')
    if out:
        print(f"STATUS: LAUNCHED SUCCESSFULLY (PID: {out})")
    else:
        print("STATUS: STILL CRASHING OR FAILED TO LAUNCH")

# 4. Check Logcat for python/kivy execution (Live Telemetry)
print("\n--- LIVE BOOT TELEMETRY (LOGCAT) ---")
out, err = run_adb('logcat -d')
logs = out.split('\n')
relevant_logs = [line for line in logs if "noir" in line.lower() or "python" in line.lower()]
for line in relevant_logs[-25:]: # Show last 25 lines
    print(line)

print("\n=== AUDIT COMPLETE ===")
