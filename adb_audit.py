import subprocess

ADB_PATH = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd_suffix):
    cmd = f'"{ADB_PATH}" {cmd_suffix}'
    print(f"\n> adb {cmd_suffix}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = res.stdout.strip()
    err = res.stderr.strip()
    if out: print(out)
    if err: print(f"ERROR: {err}")
    return out

print("=== NOIR SOVEREIGN ADB DEEP AUDIT ===")

# 1. Device Check
run_adb("devices")

# 2. Check if App is running
run_adb('shell "ps -A | grep noir"')

# 3. Read the Global Crash Protector log
print("\n--- GLOBAL CRASH PROTECTOR LOG ---")
run_adb('shell "cat /sdcard/noir_debug.txt"')

# 4. Check Recent System Logs for the App
print("\n--- RECENT LOGCAT (Filtered for python/noir) ---")
run_adb('logcat -d | grep -iE "python|noir|sovereign" | tail -n 20')

print("\n=== AUDIT COMPLETE ===")
