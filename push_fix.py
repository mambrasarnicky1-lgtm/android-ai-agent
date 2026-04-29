import subprocess

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)

run_cmd("git add mobile_app/main.py")
run_cmd('git commit -m "fix(mobile): Remove psutil dependency causing instant crash on HyperOS"')
run_cmd("git push origin main")
