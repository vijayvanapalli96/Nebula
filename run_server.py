import subprocess, sys, os
os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
subprocess.run([
    sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"
])
