import subprocess
from pathlib import Path
import os

KNIME_EXE = "/Applications/KNIME 5.4.2.app/Contents/Eclipse/knime"
WORKFLOW_PATH = Path(__file__).resolve().parent.parent / "knime" / "core-v1.knwf"

print(f"KNIME binary exists: {Path(KNIME_EXE).exists()}")
print(f"Workflow file exists: {WORKFLOW_PATH.exists()}")
print(f"Workflow path: {WORKFLOW_PATH}")

result = subprocess.run(
    [KNIME_EXE, "--help"],
    capture_output=True,
    text=True
)
print(f"Return code: {result.returncode}")
print(f"STDOUT: {result.stdout[:500]}")
print(f"STDERR: {result.stderr[:500]}")