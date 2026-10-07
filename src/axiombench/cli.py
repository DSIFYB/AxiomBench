"""Export prompts, collect API answers, and grade a complete attempt."""
import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from . import __version__
from .core import (aggregate, digest, docker_image_id, load_tasks, overall_score, prompt_for,
                   score_cpp, score_text, select_tasks)
from .report import write_html


def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def headers_for_api():
    headers = {"Content-Type":"application/json"}
    key=os.environ.get('AXIOMBENCH_API_KEY','')
    if key:headers['Authorization']='Bearer '+key
    return headers


def model_ids(base_url):
    request=urllib.request.Request(base_url.rstrip('/')+'/models',headers=headers_for_api())
    with urllib.request.urlopen(request,timeout=15) as response:
        body=response.read(1048577)
    if len(body)>1048576:raise ValueError('Model list too large')
    data=json.loads(body)
    return [row['id'] for row in data['data'] if isinstance(row.get('id'),str)]


def api_run(tasks, args):
    target = Path(args.output)
    meta_path=Path(str(target)+'.meta.json')
    completed=set()
    if not args.model:
        ids=model_ids(args.base_url)
        if len(ids)!=1:raise ValueError('Use the models command, then specify --model; automatic selection requires exactly one model')
        args.model=ids[0]
    identity={"suite_sha256":digest(args.suite),"track":args.track,"profile":args.profile,
              "selected_ids_sha256":hashlib.sha256('\n'.join(t['id'] for t in tasks).encode()).hexdigest(),
              "model":args.model,"base_url":args.base_url,"temperature":args.temperature,"max_tokens":args.max_tokens}
    if args.resume:
        if not target.exists() or not meta_path.exists():raise ValueError('--resume requires both existing answers and metadata')
        previous=json.loads(meta_path.read_text(encoding='utf-8'))
        if any(previous.get(k)!=v for k,v in identity.items()):raise ValueError('Resume configuration mismatch')
        for line in target.read_text(encoding='utf-8').splitlines():
            row=json.loads(line)
            if row['id'] in completed or row['id'] not in {t['id'] for t in tasks}:raise ValueError('Invalid saved attempt')
            completed.add(row['id'])
    elif target.exists() or meta_path.exists():
        raise ValueError("Choose a new output path or use --resume with the same configuration")
    target.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"version": __version__, **identity,
                "attempts": 1, "tools": "none",
                "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "python": platform.python_version()}
    if not args.resume:dump(meta_path, metadata)
    error=False
    with target.open("a" if args.resume else "x", encoding="utf-8") as handle:
        for index,task in enumerate(tasks,1):
            if task['id'] in completed:continue
            prompt = prompt_for(task)
            payload = {"model": args.model, "messages": [{"role": "user", "content": prompt}],
                       "temperature": args.temperature, "max_tokens": args.max_tokens, "stream": False}
            request = urllib.request.Request(args.base_url.rstrip("/") + "/chat/completions",
                                             data=json.dumps(payload).encode(), headers=headers_for_api())
            start = time.monotonic()
            row = {"id": task["id"], "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
            try:
                with urllib.request.urlopen(request, timeout=args.timeout) as response:
                    raw = response.read(8*1024*1024 + 1)
                if len(raw) > 8*1024*1024:
                    raise ValueError("API response exceeds 8 MiB")
                result = json.loads(raw)
                row["response"] = result["choices"][0]["message"]["content"]
                if not isinstance(row["response"], str):
                    raise ValueError("API did not return text content")
                row["usage"] = result.get("usage")
                row["finish_reason"] = result["choices"][0].get("finish_reason")
            except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, IndexError):
                # Do not expose provider messages or credentials. Never retry wrong answers.
                row["response"] = ""
                row["error"] = "api_error"
                error=True
            row["latency_seconds"] = round(time.monotonic() - start, 3)
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            print(f'[{index}/{len(tasks)}] '+task["id"] + (" API ERROR" if row.get("error") else " collected"),flush=True)
            if error:break
    return 2 if error else 0


def grade(tasks, args):
    predictions = {}
    for line in Path(args.predictions).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("id") in predictions or not isinstance(row.get("response"), str):
            raise ValueError("Duplicate id or non-text response in predictions")
        predictions[row["id"]] = row
    unknown = predictions.keys() - {t["id"] for t in tasks}
    if unknown:
        raise ValueError(f"Unknown or out-of-track ids: {sorted(unknown)}")
    metadata = None
    meta_path = Path(args.predictions + ".meta.json")
    if meta_path.exists():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        selected_hash=hashlib.sha256('\n'.join(t['id'] for t in tasks).encode()).hexdigest()
        if metadata.get("suite_sha256") != digest(args.suite) or metadata.get("track") != args.track or metadata.get('profile','quick')!=args.profile:
            raise ValueError("Attempt metadata does not match suite hash, track or profile")
        if metadata.get('selected_ids_sha256',selected_hash)!=selected_hash:raise ValueError('Selected IDs mismatch')
    image = None
    if any(t["kind"] == "cpp" and predictions.get(t["id"], {}).get("response") for t in tasks):
        image = docker_image_id(args.image)
    rows = []
    for index,task in enumerate(tasks,1):
        row = predictions.get(task["id"])
        if row is None:
            score = {"passed": False, "status": "missing"}
        elif row.get("error"):
            score = {"passed": False, "status": "api_error"}
        else:
            expected_prompt_hash = hashlib.sha256(prompt_for(task).encode()).hexdigest()
            if "prompt_sha256" in row and row["prompt_sha256"] != expected_prompt_hash:
                raise ValueError(f"Prompt mismatch for {task['id']}")
            if task["kind"] == "cpp":
                score = score_cpp(task, row["response"], image)
            else:
                score = score_text(task, row["response"])
        rows.append({"id": task["id"], "track": task["track"], "category": task["category"],
                     "difficulty": task["difficulty"], "family":task.get('family',task['id']),
                     "mode": task.get("mode"), "repair_type":task.get('repair_type'), **score})
        if task['kind']=='cpp':print(f'Grading [{index}/{len(tasks)}] {task["id"]}: {score["status"]}',flush=True)
    report = {"axiombench_version": __version__, "suite_sha256": digest(args.suite),
              "predictions_sha256": digest(args.predictions), "track": args.track, 'profile':args.profile,
              "run_metadata": metadata, "docker_image_id": image,
              "note": "Development set. Not an official external benchmark score or an IQ measurement.",
              "summary": aggregate(rows), "overall": overall_score(rows),
              "cpp_modes": {mode: aggregate([r for r in rows if r.get("mode") == mode])["cpp"]
                            for mode in ("generation", "repair")},
              "cpp_repair_types": {kind: aggregate([r for r in rows if r.get('mode')=='repair' and r.get('repair_type')==kind])['cpp']
                                   for kind in ('semantic','syntax')},
              "tasks": rows}
    dump(args.output, report)
    html_path=str(Path(args.output).with_suffix('.html'))
    write_html(html_path,report)
    print('HTML report: '+html_path)
    print('Overall score: '+json.dumps(report['overall'], ensure_ascii=False))
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 2 if any(r["status"] in {"api_error", "missing"} for r in rows) else 0


def main():
    parser = argparse.ArgumentParser(prog="axiombench")
    parser.add_argument("--suite", default="benchmarks/quality-v0.3/tasks.jsonl.gz")
    parser.add_argument("--track", choices=["all", "general", "cpp", "math"], default="all")
    parser.add_argument('--profile',choices=['quick','full'],default='quick')
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    models=commands.add_parser('models')
    models.add_argument('--base-url',default='http://127.0.0.1:1234/v1')
    export = commands.add_parser("export")
    export.add_argument("--output", required=True)
    run = commands.add_parser("run")
    run.add_argument("--base-url", default="http://127.0.0.1:1234/v1")
    run.add_argument("--model")
    run.add_argument('--resume',action='store_true')
    run.add_argument("--temperature", type=float, default=0.0)
    run.add_argument("--max-tokens", type=int, default=2048)
    run.add_argument("--timeout", type=float, default=180)
    run.add_argument("--output", required=True)
    grading = commands.add_parser("grade")
    grading.add_argument("--predictions", required=True)
    grading.add_argument("--output", required=True)
    grading.add_argument("--image", default="gcc:14")
    args = parser.parse_args()
    try:
        if args.command=='models':
            print('\n'.join(model_ids(args.base_url)))
            return 0
        tasks = load_tasks(args.suite)
        tasks = select_tasks(tasks,args.track,args.profile)
        if not tasks:
            raise ValueError("No tasks in selected track")
        if args.command == "validate":
            print(f"Validated {len(tasks)} tasks; sha256={digest(args.suite)}")
        elif args.command == "export":
            write_jsonl(args.output, [{"id": t["id"], "track": t["track"], "prompt": prompt_for(t)} for t in tasks])
            print(f"Exported {len(tasks)} prompts")
        elif args.command == "run":
            if args.max_tokens < 1 or args.timeout <= 0:
                raise ValueError("Token and timeout limits must be positive")
            return api_run(tasks, args)
        else:
            return grade(tasks, args)
    except (ValueError, KeyError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


# Exposed through `python -m axiombench.cli` and the console script.
if __name__ == "__main__":
    sys.exit(main())
