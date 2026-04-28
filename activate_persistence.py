import subprocess
import os

def run_adb(cmd):
    try:
        res = subprocess.run(f"C:\\Users\\ASUS\\platform-tools\\adb.exe {cmd}", shell=True, capture_output=True, text=True)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def apply_persistence():
    print("[INIT] NOIR SOVEREIGN: NEURAL PERSISTENCE ACTIVATOR")
    print("---------------------------------------------")
    pkg = "org.noir.sovereign"
    
    # 1. Disable Battery Optimization
    print("[*] Disabling Battery Optimization...")
    run_adb(f"shell dumpsys deviceidle whitelist +{pkg}")
    
    # 2. Grant Background Execution
    print("[*] Granting Background Execution rights...")
    run_adb(f"shell cmd appops set {pkg} RUN_IN_BACKGROUND allow")
    
    # 3. Standby Bucket
    print("[*] Setting Standby Bucket to ACTIVE...")
    run_adb(f"shell am set-standby-bucket {pkg} active")
    
    # 4. Critical Permissions
    print("[*] Granting critical permissions...")
    perms = [
        "android.permission.POST_NOTIFICATIONS",
        "android.permission.WAKE_LOCK",
        "android.permission.SYSTEM_ALERT_WINDOW",
        "android.permission.PACKAGE_USAGE_STATS"
    ]
    for p in perms:
        run_adb(f"shell pm grant {pkg} {p}")
        
    print("\n[DONE] NEURAL PERSISTENCE ACTIVE.")

if __name__ == "__main__":
    apply_persistence()
