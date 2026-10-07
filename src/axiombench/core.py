"""Strict data loading, objective scoring and Docker-only C++ judging."""
import hashlib
import gzip
import json
import math
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

TRACKS = {"general", "cpp", "math"}
KINDS = {"json", "number", "cpp"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_tasks(path):
    tasks = []
    seen = set()
    fixtures = {}
    suite_root = Path(path).resolve().parent
    content = gzip.decompress(Path(path).read_bytes()).decode("utf-8") if str(path).endswith('.gz') else Path(path).read_text(encoding="utf-8")
    for line_no, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        task = json.loads(line)
        required = {"id", "track", "kind", "prompt", "category", "difficulty",
                    "source", "license", "split", "created_at"}
        missing = required - task.keys()
        if missing:
            raise ValueError(f"Line {line_no}: missing {sorted(missing)}")
        if not isinstance(task["id"], str) or not task["id"] or task["id"] in seen:
            raise ValueError(f"Line {line_no}: invalid or duplicate id")
        seen.add(task["id"])
        if task["track"] not in TRACKS or task["kind"] not in KINDS:
            raise ValueError(f"{task['id']}: invalid track/kind")
        if (task["track"] == "cpp") != (task["kind"] == "cpp"):
            raise ValueError(f"{task['id']}: inconsistent C++ kind")
        if task["difficulty"] not in {"basic", "intermediate", "advanced"}:
            raise ValueError(f"{task['id']}: invalid difficulty")
        if task["split"] not in {"dev", "eval"}:
            raise ValueError(f"{task['id']}: invalid split")
        for key in ("prompt", "source", "license", "category", "created_at"):
            if not isinstance(task[key], str) or not task[key].strip():
                raise ValueError(f"{task['id']}: invalid {key}")
        if task["kind"] == "cpp":
            cpu_limit=task.get('cpu_time_limit_seconds',10)
            if type(cpu_limit) is not int or not 1<=cpu_limit<=10:
                raise ValueError(f"{task['id']}: invalid CPU limit")
            if task.get("mode") not in {"generation", "repair"}:
                raise ValueError(f"{task['id']}: invalid C++ mode")
            if task["mode"] == "repair" and not task.get("buggy_code"):
                raise ValueError(f"{task['id']}: repair needs buggy_code")
            tests = task.get("tests", [])
            for case in tests:
                for key in ('stdin','stdout'):
                    reference=case.get(key+'_fixture')
                    if reference is None:continue
                    fixture=(suite_root/reference['path']).resolve()
                    if not fixture.is_relative_to(suite_root/'fixtures'):
                        raise ValueError(f"{task['id']}: fixture outside fixture directory")
                    cache_key=(str(fixture),reference['sha256'])
                    if cache_key not in fixtures:
                        raw=fixture.read_bytes()
                        if hashlib.sha256(raw).hexdigest()!=reference['sha256']:
                            raise ValueError(f"{task['id']}: fixture checksum mismatch")
                        fixtures[cache_key]=gzip.decompress(raw).decode('utf-8')
                    case[key]=fixtures[cache_key]
            if not tests or any(not isinstance(t.get(k), str) for t in tests for k in ("stdin", "stdout")):
                raise ValueError(f"{task['id']}: invalid tests")
        elif "answer" not in task:
            raise ValueError(f"{task['id']}: missing answer")
        elif task["kind"] == "number":
            parse_number(str(task["answer"]))
        tasks.append(task)
    if not tasks:
        raise ValueError("Empty suite")
    return tasks


def prompt_for(task):
    text = task["prompt"]
    if task["kind"] == "cpp":
        if task["mode"] == "repair":
            text += "\nКод с ошибкой:\n```cpp\n" + task["buggy_code"] + "\n```"
        return text + "\nВерни полный исходный файл C++20 одним блоком ```cpp ... ```."
    if task["kind"] == "number":
        return text + '\nВерни только JSON вида {"answer":"число или дробь p/q"}.'
    return text + '\nВерни только JSON вида {"answer":...}; тип и порядок элементов значимы.'


def select_tasks(tasks, track='all', profile='quick'):
    tasks = [t for t in tasks if track == 'all' or t['track'] == track]
    if profile == 'full':
        return tasks
    seen = set()
    result = []
    for task in tasks:
        key = (task.get('family', task['id']), task.get('mode'))
        if key not in seen:
            seen.add(key)
            result.append(task)
    return result


def parse_number(value):
    if len(value) > 256 or not re.fullmatch(r"[+-]?\d+(?:/\d+|\.\d+(?:[eE][+-]?\d{1,3})?|[eE][+-]?\d{1,3})?", value):
        raise ValueError("Expected a finite decimal, integer or rational number")
    return Fraction(value)


def exact_equal(left, right):
    # bool is a subclass of int in Python: JSON true must not pass for 1.
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(exact_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(exact_equal(a, b) for a, b in zip(left, right))
    return left == right


def score_text(task, response):
    try:
        value = json.loads(response, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        if not isinstance(value, dict) or set(value) != {"answer"}:
            raise ValueError("Expected exactly one answer key")
        if task["kind"] == "number":
            if type(value["answer"]) not in (str, int, float):
                raise ValueError("Invalid numeric answer")
            correct = parse_number(str(value["answer"])) == parse_number(str(task["answer"]))
        else:
            correct = exact_equal(value["answer"], task["answer"])
        return {"passed": correct, "status": "pass" if correct else "wrong_answer"}
    except (ValueError, TypeError, ZeroDivisionError):
        return {"passed": False, "status": "invalid_format"}


def extract_cpp(response):
    blocks = re.findall(r"```(?:cpp|c\+\+)\s*\n(.*?)```", response, flags=re.DOTALL)
    if len(blocks) != 1 or len(blocks[0].encode()) > 131072:
        raise ValueError("Expected one C++ block, at most 128 KiB")
    return blocks[0]


def docker_image_id(image):
    if shutil.which("docker") is None:
        raise RuntimeError("Docker is required for C++ grading; host execution is disabled")
    result = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", image],
                            capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise RuntimeError(f"Docker image unavailable; run: docker pull {image}")
    return result.stdout.strip()


def bounded_process(command, stdin, limit_seconds=20, max_output=1048576):
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err, tempfile.TemporaryFile() as inp:
        inp.write(stdin.encode())
        inp.seek(0)
        proc = subprocess.Popen(command, stdin=inp, stdout=out, stderr=err)
        started = time.monotonic()
        status = None
        while proc.poll() is None:
            if time.monotonic() - started > limit_seconds:
                status = "timeout"
            elif out.tell() > max_output or err.tell() > max_output:
                status = "output_limit"
            if status:
                proc.kill()
                break
            time.sleep(0.02)
        proc.wait()
        if out.tell() > max_output or err.tell() > max_output:
            status = status or "output_limit"
        out.seek(0)
        err.seek(0)
        return proc.returncode, out.read(max_output).decode(errors="replace"), err.read(max_output).decode(errors="replace"), status


def score_cpp(task, response, image):
    try:
        source = extract_cpp(response)
    except ValueError:
        return {"passed": False, "status": "invalid_format"}
    # Compile once to a private named volume; fresh runtime container for each test.
    tests = []
    with tempfile.TemporaryDirectory(prefix="axiombench-") as folder:
        path = Path(folder)
        path.chmod(0o755)
        (path / "main.cpp").write_text(source, encoding="utf-8")
        (path / "main.cpp").chmod(0o644)
        volume = 'axiombench-build-' + uuid.uuid4().hex
        created = subprocess.run(['docker', 'volume', 'create', volume], capture_output=True, text=True, timeout=10)
        if created.returncode:
            raise RuntimeError('Docker volume creation failed')
        def command(name, compile_mode=False):
            cpu_limit=10 if compile_mode else task.get('cpu_time_limit_seconds',10)
            base = ["docker", "run", "--name", name, "--network=none",
                    "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
                    "--memory=512m", "--memory-swap=512m", "--cpus=1", "--pids-limit=64",
                    f"--ulimit=cpu={cpu_limit}:{cpu_limit}", "--ulimit=fsize=16777216:16777216", "--ulimit=nofile=64:64",
                    "--tmpfs=/tmp:rw,exec,nosuid,size=64m,mode=1777"]
            if compile_mode:
                return base + ['--mount', f'type=bind,src={path},dst=/src,readonly',
                               '--mount', f'type=volume,src={volume},dst=/build', image,
                               'g++', '-std=c++20', '-O2', '/src/main.cpp', '-o', '/build/prog']
            return base + ['--user=65534:65534', '--mount', f'type=volume,src={volume},dst=/solution,readonly',
                           '-i', image, '/solution/prog']
        def execute(cmd, name, stdin, seconds):
            try:
                result = bounded_process(cmd, stdin, limit_seconds=seconds)
                if result[0] in (125, 126, 127):
                    state=subprocess.run(['docker','inspect','--format','{{.State.Error}}',name],capture_output=True,text=True,timeout=10)
                    if state.returncode or state.stdout.strip():
                        raise RuntimeError('Docker infrastructure or executable launch failed: '+result[2][:200])
            finally:
                subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)
            return result
        try:
            name = "axiombench-" + uuid.uuid4().hex
            code, output, error, status = execute(command(name, True), name, '', 45)
            if code or status:
                return {'passed':False, 'status':status or 'compile_error'}
            for case in task['tests']:
                name = 'axiombench-' + uuid.uuid4().hex
                code, output, error, status = execute(command(name), name, case['stdin'], 15)
                passed = status is None and code == 0 and output.split() == case['stdout'].split()
                tests.append({'passed':passed, 'exit_code':code,
                              'status':status or ('pass' if passed else 'runtime_or_answer_error')})
                if not passed:
                    break  # Task is already failed; don't spend time on remaining hidden cases.
        finally:
            subprocess.run(['docker','volume','rm','-f',volume],capture_output=True,timeout=10)
    passed = all(t["passed"] for t in tests)
    return {"passed": passed, "status": "pass" if passed else "failed_tests", "tests": tests,
            'total_test_cases': len(task['tests']), 'executed_test_cases': len(tests)}


def wilson(passed, total):
    if not total:
        return None
    z = 1.96
    p = passed / total
    d = 1 + z*z/total
    center = (p + z*z/(2*total)) / d
    radius = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / d
    return [round(100*(center-radius), 2), round(100*(center+radius), 2)]


def aggregate(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["track"]].append(row)
    result = {}
    for track in sorted(TRACKS):
        group = groups[track]
        total = len(group)
        passed = sum(r["passed"] for r in group)
        families = defaultdict(list)
        for r in group:
            families[r.get('family', r.get('id','item'))].append(r)
        family_rates = [sum(r['passed'] for r in f)/len(f) for f in families.values()]
        clustered = any(len(f)>1 for f in families.values())
        result[track] = {"total": total, "passed": passed,
                         "accuracy_percent": round(100*passed/total, 2) if total else None,
                         "wilson_95_percent": None if clustered else wilson(passed, total),
                         'family_count':len(families),
                         'family_macro_accuracy_percent':round(100*sum(family_rates)/len(family_rates),2) if family_rates else None,
                         'confidence_note':'Dependent family variants; IID Wilson interval suppressed' if clustered else 'IID assumption; public development set',
                         "statuses": dict(Counter(r["status"] for r in group))}
    return result


def overall_score(rows):
    """Equal weight for four dimensions; never renormalize a partial track run."""
    groups = {
        'general': [r for r in rows if r['track'] == 'general'],
        'math': [r for r in rows if r['track'] == 'math'],
        **{f'cpp_{mode}': [r for r in rows if r['track'] == 'cpp' and r.get('mode') == mode]
           for mode in ('generation', 'repair')},
    }
    absent = [key for key, group in groups.items() if not group]
    incomplete = sum(r['status'] in {'missing', 'api_error'} for r in rows)
    value = None if absent else 25 * sum(
        (Fraction(sum(r['passed'] for r in group), len(group)) for group in groups.values()),
        Fraction(0))
    return {
        'protocol': 'equal-four-v1', 'weights': {key: 0.25 for key in groups},
        'score': round(float(value), 2) if value is not None else None,
        'display_score': math.floor(value + Fraction(1, 2)) if value is not None else None,
        'maximum': 100, 'missing_dimensions': absent, 'incomplete_tasks': incomplete,
        'status': 'unavailable' if absent else ('provisional' if incomplete else 'complete'),
        'comparable': not absent and not incomplete,
    }
