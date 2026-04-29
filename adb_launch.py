import subprocess
import time

ADB_PATH = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd_suffix):
    cmd = f'"{ADB_PATH}" {cmd_suffix}'
    print(f"\n> adb {cmd_suffix}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = res.stdout.strip()
    err = res.stderr.strip()
    return out, err

print("=== NOIR SOVEREIGN LAUNCH & AUDIT ===")

# 1. Clear previous logs to avoid noise
run_adb("logcat -c")

# 2. Forcibly Launch the App
print("\n[+] Launching APK on Redmi Note 14...")
out, err = run_adb('shell monkey -p org.noir.sovereign.noir_sovereign -c android.intent.category.LAUNCHER 1')
if out: print(out)
if err: print(err)

# 3. Wait for boot sequence
print("\n[+] Waiting 5 seconds for boot sequence and neural handshake...")
time.sleep(5)

# 4. Dump Logcat
print("\n[+] Capturing Logcat...")
out, err = run_adb("logcat -d")
logs = out.split('\n')

print("\n--- CRITICAL BOOT LOGS ---")
noir_logs = [line for line in logs if "noir" in line.lower() or "sovereign" in line.lower() or "python" in line.lower() or "kivy" in line.lower()]
for line in noir_logs[-30:]: # Show last 30 relevant lines
    print(line)

# 5. Check if process is alive
print("\n--- PROCESS STATUS ---")
out, err = run_adb('shell "pidof org.noir.sovereign.noir_sovereign"')
if out:
    print(f"STATUS: RUNNING (PID: {out})")
else:
    print("STATUS: NOT RUNNING / CRASHED")

print("\n=== AUDIT COMPLETE ===")
