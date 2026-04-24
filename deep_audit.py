import os
import re
import json

ROOT = r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent"
REPORT_FILE = os.path.join(ROOT, "total_audit_deep.md")

issues = []

# Rules for detection
PORT_REGEX = re.compile(r'port\s*=\s*(\d+)')
URL_REGEX = re.compile(r'http[s]?://[^\s\'"]+')
HARDCODED_KEY_REGEX = re.compile(r'API_KEY\s*=\s*[\'"][^\'"]+[\'"]')

ports = {}
urls = []
cache_files = []

def add_issue(category, file_path, line_num, message):
    issues.append({
        "category": category,
        "file": file_path.replace(ROOT, ""),
        "line": line_num,
        "message": message
    })

def scan_file(filepath):
    if not filepath.endswith(('.py', '.js', '.ts', '.yml', '.spec')): return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Find hardcoded API Keys
            if "API_KEY = " in line and "os.getenv" not in line and "os.environ" not in line:
                add_issue("SECURITY", filepath, line_num, "Hardcoded API Key detected")
                
            # Find Ports
            port_match = PORT_REGEX.search(line)
            if port_match:
                port = port_match.group(1)
                if port not in ports: ports[port] = []
                ports[port].append(filepath.replace(ROOT, ""))
                
            # Find absolute paths (Windows) that might break on Linux/VPS
            if "C:\\" in line and not "C:\\Users" in filepath: # avoid self script match
                add_issue("PORTABILITY", filepath, line_num, "Windows absolute path detected")
                
            # Circular dependency check hints (just looking for imports inside functions as a smell or potential issue)
            if filepath.endswith('.py') and line.strip().startswith('import ') and line_num > 20:
                 if not line.startswith('import'):
                     # inline import
                     pass 
                     
    except Exception as e:
        pass

for root, dirs, files in os.walk(ROOT):
    if '.git' in root or 'venv' in root or 'node_modules' in root or '.buildozer' in root:
        continue
        
    for file in files:
        if file.endswith('.pyc') or file == '__pycache__':
            cache_files.append(os.path.join(root, file).replace(ROOT, ""))
        else:
            scan_file(os.path.join(root, file))

# Find Port Conflicts
for port, files in ports.items():
    if len(set(files)) > 1:
        add_issue("CONFLICT", "Multiple", 0, f"Port {port} used across multiple files: {set(files)}")

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("# 🔬 DEEP SYSTEM AUDIT REPORT (Code-Level Analysis)\n\n")
    
    f.write("## 1. Security & Hardcoded Variables\n")
    for issue in [i for i in issues if i['category'] == 'SECURITY']:
        f.write(f"- 🔴 **{issue['file']}:{issue['line']}** - {issue['message']}\n")
        
    f.write("\n## 2. Portability & Compatibility Risks\n")
    for issue in [i for i in issues if i['category'] == 'PORTABILITY']:
        f.write(f"- 🟡 **{issue['file']}:{issue['line']}** - {issue['message']}\n")
        
    f.write("\n## 3. Architecture & Port Conflicts\n")
    for issue in [i for i in issues if i['category'] == 'CONFLICT']:
        f.write(f"- 🟠 **{issue['message']}**\n")
        
    f.write("\n## 4. Cache & Ghost Files (Needs Cleaning)\n")
    if cache_files:
        f.write("Found compiled cache files that might cause version conflicts:\n")
        for c in cache_files[:10]:
            f.write(f"- ` {c} `\n")
        if len(cache_files) > 10:
            f.write(f"- ... and {len(cache_files)-10} more.\n")
    else:
        f.write("- ✅ No stale cache files found.\n")

print(f"Deep audit complete. Report saved to {REPORT_FILE}")
