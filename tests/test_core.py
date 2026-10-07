import json
import math
import unittest
from pathlib import Path
from axiombench.core import (aggregate, digest, exact_equal, extract_cpp, load_tasks,
                            parse_number, prompt_for, score_text, wilson)

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "benchmarks/starter-v0.1/tasks.jsonl"


class ScoringTests(unittest.TestCase):
    def test_manifest_checksums(self):
        manifest = json.loads((SUITE.parent / "manifest.json").read_text())
        for relative_path, checksum in manifest["files"].items():
            self.assertEqual(digest(SUITE.parent / relative_path), checksum)

    def test_exact_rationals(self):
        task = {"kind": "number", "answer": "1/2"}
        for value in ["2/4", "0.50", 0.5, "5e-1"]:
            self.assertTrue(score_text(task, json.dumps({"answer": value}))["passed"])
        self.assertFalse(score_text(task, '{"answer":"0.5001"}')["passed"])

    def test_no_code_execution_in_math(self):
        for value in ["__import__('os').system('whoami')", "1+1", "nan", "1/0"]:
            self.assertEqual(score_text({"kind": "number", "answer": "2"}, json.dumps({"answer": value}))["status"], "invalid_format")

    def test_strict_format(self):
        task = {"kind": "json", "answer": True}
        for response in ['true', '{"answer":true,"extra":1}', 'Answer: {"answer":true}', '{"answer":NaN}']:
            self.assertEqual(score_text(task, response)["status"], "invalid_format")

    def test_types_and_order(self):
        self.assertFalse(exact_equal(True, 1))
        self.assertFalse(exact_equal([1, 2], [2, 1]))
        self.assertFalse(exact_equal({"x": [True]}, {"x": [1]}))
        self.assertTrue(exact_equal({"x": [True]}, {"x": [True]}))

    def test_cpp_extraction(self):
        self.assertEqual(extract_cpp('```cpp\nint main(){}\n```').strip(), 'int main(){}')
        with self.assertRaises(ValueError):
            extract_cpp('```cpp\na\n```\n```cpp\nb\n```')

    def test_missing_in_denominator(self):
        summary = aggregate([{"track": "general", "passed": True, "status": "pass"},
                             {"track": "general", "passed": False, "status": "missing"}])
        self.assertEqual(summary["general"]["accuracy_percent"], 50)
        self.assertIsNone(summary["math"]["accuracy_percent"])

    def test_confidence_interval(self):
        low, high = wilson(5, 10)
        self.assertLess(low, 50)
        self.assertGreater(high, 50)
        self.assertIsNone(wilson(0, 0))

    def test_public_prompts_exclude_answers_tests_references(self):
        tasks = load_tasks(SUITE)
        self.assertEqual(len(tasks), 32)
        for task in tasks:
            prompt = prompt_for(task)
            self.assertNotIn('"tests"', prompt)
            self.assertNotIn("references/", prompt)
            if task["kind"] == "cpp" and task["mode"] == "repair":
                self.assertIn(task["buggy_code"], prompt)

    def test_math_answers_with_independent_oracles(self):
        import itertools
        tasks = {t["id"]: t for t in load_tasks(SUITE)}
        oracles = {
            "math-003": sum("11" not in "".join(t) for t in itertools.product("01", repeat=5)),
            "math-005": pow(7, 123, 13),
            "math-009": sum(all(i != x for i, x in enumerate(p, 1)) for p in itertools.permutations(range(1, 6))),
            "math-011": next(x for x in range(1, 316) if x % 5 == 2 and x % 7 == 3 and x % 9 == 4),
        }
        for task_id, answer in oracles.items():
            self.assertEqual(parse_number(tasks[task_id]["answer"]), answer)


if __name__ == "__main__":
    unittest.main()
