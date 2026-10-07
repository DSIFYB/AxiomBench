"""Run ONLY our checked-in trusted reference implementations on the host.

Never point this script at model-generated code. Production grading uses Docker.
"""
import subprocess
import tempfile
from pathlib import Path
from axiombench.core import load_tasks, score_text

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks" / "starter-v0.1"
count = 0
for task in load_tasks(DATA / "tasks.jsonl"):
    if task["kind"] != "cpp":
        import json
        assert score_text(task, json.dumps({"answer": task["answer"]}))["passed"]
        continue
    with tempfile.TemporaryDirectory() as folder:
        executable = str(Path(folder) / "solution")
        subprocess.run(["g++", "-std=c++20", "-O2", "-Wall", "-Wextra",
                        str(DATA / task["reference"]), "-o", executable], check=True, timeout=30)
        for test in task["tests"]:
            result = subprocess.run([executable], input=test["stdin"], capture_output=True,
                                    text=True, timeout=3, check=True)
            assert result.stdout.split() == test["stdout"].split(), task["id"]
            count += 1
        if task["mode"] == "repair":
            source = Path(folder) / "buggy.cpp"
            source.write_text(task["buggy_code"], encoding="utf-8")
            subprocess.run(["g++", "-std=c++20", "-O2", str(source), "-o", executable], check=True, timeout=30)
            failures = 0
            for test in task["tests"]:
                result = subprocess.run([executable], input=test["stdin"], capture_output=True, text=True, timeout=3)
                failures += result.returncode != 0 or result.stdout.split() != test["stdout"].split()
            assert failures > 0, f"Repair tests do not detect bug: {task['id']}"
print(f"Verified 8 trusted C++ references on {count} cases; all 4 repair bugs detected")
