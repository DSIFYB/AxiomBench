import contextlib
import io
import json
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from axiombench.cli import main
from axiombench.core import load_tasks

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "benchmarks/starter-v0.1/tasks.jsonl"


class CliTests(unittest.TestCase):
    def invoke(self, arguments):
        with patch("sys.argv", ["axiombench", "--suite", str(SUITE), *arguments]):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return main()

    def test_export_and_missing_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            exported = Path(tmp) / "prompts.jsonl"
            self.assertEqual(self.invoke(["--track", "math", "export", "--output", str(exported)]), 0)
            rows = [json.loads(line) for line in exported.read_text().splitlines()]
            self.assertEqual(len(rows), 12)
            self.assertEqual(set(rows[0]), {"id", "track", "prompt"})
            predictions = Path(tmp) / "predictions.jsonl"
            predictions.write_text('')
            report = Path(tmp) / "report.json"
            self.assertEqual(self.invoke(["--track", "math", "grade", "--predictions", str(predictions), "--output", str(report)]), 2)
            summary = json.loads(report.read_text())["summary"]["math"]
            self.assertEqual(summary["total"], 12)
            self.assertEqual(summary["statuses"], {"missing": 12})

    def test_mock_api_end_to_end_and_no_overwrite(self):
        expected = {t["prompt"]: t["answer"] for t in load_tasks(SUITE) if t["track"] == "math"}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                prompt = payload["messages"][0]["content"].split('\nВерни только JSON')[0]
                data = json.dumps({"choices": [{"message": {"content": json.dumps({"answer": expected[prompt]})}, "finish_reason": "stop"}]}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                predictions = str(Path(tmp) / "attempt.jsonl")
                report = str(Path(tmp) / "report.json")
                args = ["--track", "math", "run", "--base-url", f"http://127.0.0.1:{server.server_port}/v1", "--model", "ci-fixture-not-a-model", "--output", predictions]
                self.assertEqual(self.invoke(args), 0)
                self.assertEqual(self.invoke(args), 1)
                before=Path(predictions).read_text()
                self.assertEqual(self.invoke(args+['--resume']),0)
                self.assertEqual(Path(predictions).read_text(),before)
                self.assertEqual(self.invoke(args+['--resume','--max-tokens','7']),1)
                self.assertEqual(self.invoke(["--track", "math", "grade", "--predictions", predictions, "--output", report]), 0)
                self.assertEqual(json.loads(Path(report).read_text())["summary"]["math"]["passed"], 12)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_duplicate_prediction_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.jsonl"
            row = json.dumps({"id": "math-001", "response": ""}) + "\n"
            path.write_text(row*2)
            self.assertEqual(self.invoke(["--track", "math", "grade", "--predictions", str(path), "--output", str(Path(tmp) / "out.json")]), 1)

    def test_prompt_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong_prompt.jsonl"
            path.write_text(json.dumps({"id": "math-001", "response": '{"answer":"31/36"}', "prompt_sha256": "bad"}))
            self.assertEqual(self.invoke(["--track", "math", "grade", "--predictions", str(path), "--output", str(Path(tmp) / "out.json")]), 1)

    def test_cpp_modes_missing_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            predictions = Path(tmp) / "missing.jsonl"
            predictions.write_text("")
            report = Path(tmp) / "report.json"
            self.assertEqual(self.invoke(["--track", "cpp", "grade", "--predictions", str(predictions), "--output", str(report)]), 2)
            data = json.loads(report.read_text())
            self.assertEqual(data["cpp_modes"]["generation"]["total"], 4)
            self.assertEqual(data["cpp_modes"]["repair"]["total"], 4)


if __name__ == "__main__":
    unittest.main()
