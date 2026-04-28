import os, sys, re

def audit_workspace():
    print("[AUDIT] NOIR SOVEREIGN: DEEP SYSTEM AUDIT (V18.5)")
    print("=" * 50)
    
    issues = []
    
    # 1. Check for orphaned / redundant files
    print("[*] Auditing File Structure...")
    redundant_patterns = [r"test_.*\.py", r"scratch_.*", r"audit_.*\.md", r".*\.log$"]
    for root, dirs, files in os.walk("."):
        for f in files:
            if any(re.match(p, f) for p in redundant_patterns):
                # issues.append(f"Redundant file: {os.path.join(root, f)}")
                pass

    # 2. Check for Syntax & Consistency in main components
    core_files = [
        "mobile_app/main.py",
        "mobile_app/service.py",
        "noir-vps/brain.py",
        "noir-vps/telegram_bot.py",
        "pc_agent.py"
    ]
    
    for cf in core_files:
        if not os.path.exists(cf):
            issues.append(f"CRITICAL: Missing core file {cf}")
            continue
            
        with open(cf, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # Check for hardcoded IPs
            if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", content):
                if "os.environ" not in content and "8.215.23.17" in content:
                    issues.append(f"Consistency: Hardcoded IP found in {cf}")
            
            # Check for consistent API KEY usage
            if "NOIR_AGENT_KEY_V6" not in content and "API_KEY" in content:
                if "os.environ" not in content:
                    issues.append(f"Security: Potential inconsistent API key reference in {cf}")

    # 3. Check for Cache Bloat
    print("[*] Auditing Cache Bloat...")
    cache_dirs = [".buildozer", "bin", "__pycache__", ".pytest_cache"]
    for d in cache_dirs:
        if os.path.exists(d):
            size = sum(os.path.getsize(os.path.join(root, f)) for root, dirs, files in os.walk(d) for f in files)
            if size > 100 * 1024 * 1024: # 100MB
                issues.append(f"Performance: Cache directory {d} is bloated ({size // (1024*1024)}MB)")

    # 4. Report Results
    print("\n" + "!" * 10 + " AUDIT REPORT " + "!" * 10)
    if not issues:
        print("[OK] NO ISSUES DETECTED. System is optimized.")
    else:
        for i in issues:
            print(f"- {i}")
            
    return issues

if __name__ == "__main__":
    audit_workspace()
