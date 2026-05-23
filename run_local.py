import os
import subprocess
import sys

backend_dir = os.path.join(os.path.dirname(__file__), "backend")

print("Starting ShopStock locally...")
print("Open: http://127.0.0.1:8000")

subprocess.run([
    sys.executable,
    "-m",
    "uvicorn",
    "main:app",
    "--reload",
    "--host",
    "127.0.0.1",
    "--port",
    "8000"
], cwd=backend_dir)