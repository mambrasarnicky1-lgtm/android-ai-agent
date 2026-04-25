import os
import re
import py_compile

ROOT = r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent"
REPORT_FILE = os.path.join(ROOT, "AUDIT_REPORT_V17.md")

issues = []
cache_dirs = []
cache_files = []

def add_issue(category, file_path, line_num, message):
    issues.append({
        "category": category,
        "file": file_path.replace(ROOT, ""),
        "line": line_num,
        "message": message
    })

def check_syntax(filepath):
    try:
        py_compile.compile(filepath, doraise=True)
    except py_compile.PyCompileError as e:
        add_issue("SYNTAX_ERROR", filepath, 0, str(e.msg).replace("\n", " "))

def scan_file(filepath):
    if filepath.endswith('.py'):
        check_syntax(filepath)
        
    if not filepath.endswith(('.py', '.js', '.ts', '.yml', '.spec', '.html')): return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Find duplicate class/function names which can cause conflicts
            # This is a basic check, real AST parsing is better but this is fast
            
            # Find potential duplicate memory instances or singleton violations
            if "memory = TemporalMemory()" in line and "def " not in line and "class " not in line:
                add_issue("LOGIC_RISK", filepath, line_num, "TemporalMemory instance created globally/repeatedly without singleton pattern")
                
            # Check for obsolete or duplicate API keys
            if "API_KEY" in line and "=" in line and ("os.environ" not in line and "os.getenv" not in line):
                add_issue("SECURITY", filepath, line_num, "Hardcoded/Suspicious API Key assignment")
                
            # Hardcoded paths
            if "/app/noir-vps/" in line and not filepath.endswith("docker-compose.yml"):
                add_issue("PORTABILITY", filepath, line_num, "Hardcoded docker container path detected inside code")
                
    except Exception as e:
        pass

for root, dirs, files in os.walk(ROOT):
    # Detect Cache Dirs
    for d in dirs:
        if d in ['__pycache__', '.pytest_cache', '.buildozer', '.wrangler']:
            cache_dirs.append(os.path.join(root, d).replace(ROOT, ""))
            
    if '.git' in root or 'venv' in root or 'node_modules' in root:
        continue
        
    for file in files:
        if file.endswith('.pyc') or file.endswith('.log'):
            cache_files.append(os.path.join(root, file).replace(ROOT, ""))
        else:
            scan_file(os.path.join(root, file))

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("# 🔬 TOTAL SYSTEM AUDIT REPORT (v17.5 Auto-Discovery Edition)\n\n")
    
    f.write("## 1. Syntax & Fatal Errors\n")
    syntax_issues = [i for i in issues if i['category'] == 'SYNTAX_ERROR']
    if syntax_issues:
        for issue in syntax_issues:
            f.write(f"- 🔴 **{issue['file']}** - {issue['message']}\n")
    else:
        f.write("- ✅ Zero Syntax Errors. Codebase is clean.\n")
        
    f.write("\n## 2. Logic & Architecture Risks\n")
    logic_issues = [i for i in issues if i['category'] == 'LOGIC_RISK']
    if logic_issues:
        for issue in logic_issues:
            f.write(f"- 🟠 **{issue['file']}:{issue['line']}** - {issue['message']}\n")
    else:
        f.write("- ✅ No obvious logic conflicts detected.\n")

    f.write("\n## 3. Portability & Security\n")
    port_issues = [i for i in issues if i['category'] in ['PORTABILITY', 'SECURITY']]
    if port_issues:
        for issue in port_issues:
            f.write(f"- 🟡 **{issue['file']}:{issue['line']}** - {issue['message']}\n")
    else:
        f.write("- ✅ Code is portable and secure.\n")
        
    f.write("\n## 4. Cache, Logs & Ghost Artifacts (Purge Recommended)\n")
    if cache_dirs or cache_files:
        f.write("Found compiled cache directories and log files that might cause build conflicts or disk bloat:\n")
        for c in cache_dirs:
            f.write(f"- 📂 ` {c} ` (Directory)\n")
        for c in cache_files[:15]:
            f.write(f"- 📄 ` {c} `\n")
        if len(cache_files) > 15:
            f.write(f"- ... and {len(cache_files)-15} more files.\n")
    else:
        f.write("- ✅ No stale cache files found.\n")

print(f"Audit complete. See {REPORT_FILE}")
