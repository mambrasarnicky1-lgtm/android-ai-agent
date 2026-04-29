import subprocess

ADB_PATH = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"

def run_adb(cmd_suffix):
    cmd = f'"{ADB_PATH}" {cmd_suffix}'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip()

print("=== CHECKING INSTALLED PACKAGES ===")
out = run_adb('shell pm list packages -3')
packages = out.split('\n')
for p in packages:
    if "noir" in p.lower() or "sovereign" in p.lower() or "test" in p.lower() or "org." in p.lower():
        print(p)

print("\n=== COMPLETE ===")
