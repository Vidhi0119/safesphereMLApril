import subprocess

try:
    print("Running app.py")
    res = subprocess.run([r'.\.venv\Scripts\python.exe', 'app.py'], capture_output=True, text=True, timeout=5)
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
except subprocess.TimeoutExpired as e:
    print("Timed out! STDOUT:")
    print(e.stdout)
    print("STDERR:")
    print(e.stderr)
except Exception as e:
    print(f"Exception: {e}")
