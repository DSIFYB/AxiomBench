import copy
import gzip
import json
import sys
import tempfile
import unittest
from collections import Counter,defaultdict
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from axiombench.core import digest,load_tasks,prompt_for,score_cpp,select_tasks
import contextlib
import io
from axiombench.cli import main as cli_main

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'benchmarks/quality-v0.3'
TASKS=load_tasks(DATA/'tasks.jsonl.gz')
sys.path.insert(0,str(ROOT/'tools'))
from verify_quality_text import BALANCED,verify_general,verify_new_math


class QualityTests(unittest.TestCase):
    def test_counts_and_unique_full_prompts(self):
        self.assertEqual(Counter(t['track'] for t in TASKS),dict(cpp=400,general=350,math=350))
        self.assertEqual(Counter(t.get('repair_type') for t in TASKS if t.get('mode')=='repair'),dict(syntax=100,semantic=150))
        self.assertEqual(len({prompt_for(t) for t in TASKS}),1100)
        self.assertEqual(len(select_tasks(TASKS)),110)
        self.assertEqual(len({t['family'] for t in TASKS}),95)

    def test_former_constant_answers_are_not_constant(self):
        groups=defaultdict(list)
        for task in TASKS:
            if task['track']=='general' and task['category'] in BALANCED:groups[task['category']].append(task['answer'])
        self.assertEqual(len(groups),10)
        for name,answers in groups.items():
            self.assertGreater(len({json.dumps(a,sort_keys=True) for a in answers}),1,name)
            if type(answers[0]) is bool:self.assertEqual(Counter(answers),{True:5,False:5})

    def test_independent_revised_answers(self):
        for task in TASKS:
            if task['track']=='math':verify_new_math(task)
            elif task['track']=='general':verify_general(task)

    def test_stress_reaches_declared_sizes_and_output_budget(self):
        sizes={'subarray_count':100000,'range_sum_mod':100000,'bfs_forbidden':100000,
               'dijkstra_fee':20000,'dsu_color':100000,'gap_subsequence':1000,'zero_one_knapsack':200}
        for name,size in sizes.items():
            for task in [t for t in TASKS if t['category']==name and t.get('mode')=='generation']:
                self.assertTrue(any(c.get('case_type')=='stress' and int(c['stdin'].split()[0])==size for c in task['tests']),task['id'])
        for task in TASKS:
            for case in task.get('tests',[]):self.assertLess(len(case['stdout'].encode()),1048576)

    def test_manifest_pins_all_fixtures(self):
        manifest=json.loads((DATA/'manifest.json').read_text())
        for name,sha in manifest['files'].items():self.assertEqual(digest(DATA/name),sha)

    def test_fixture_tampering_and_path_escape_rejected(self):
        task=next(t for t in TASKS if t['category']=='subarray_count')
        case=next(c for c in task['tests'] if c.get('case_type')=='stress')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'fixtures').mkdir()
            row=copy.deepcopy(task);row['tests']=[copy.deepcopy(case)]
            row['tests'][0].pop('stdout_fixture',None)
            row['tests'][0]['stdin_fixture']={'path':'fixtures/bad.gz','sha256':'0'*64}
            (root/'fixtures/bad.gz').write_bytes(gzip.compress(b'1\n0\n'))
            suite=root/'tasks.jsonl';suite.write_text(json.dumps(row))
            with self.assertRaisesRegex(ValueError,'checksum'):load_tasks(suite)
            row['tests'][0]['stdin_fixture']['path']='../outside.gz'
            suite.write_text(json.dumps(row))
            with self.assertRaisesRegex(ValueError,'outside'):load_tasks(suite)

    def test_runtime_cpu_limit_applied_without_changing_compile_budget(self):
        task=next(t for t in TASKS if t.get('repair_type')=='syntax')
        commands=[]
        def run(cmd,stdin,**kw):
            commands.append(cmd)
            return (0,'','',None) if 'g++' in cmd else (0,task['tests'][len(commands)-2]['stdout'],'',None)
        with patch('axiombench.core.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')):
            with patch('axiombench.core.bounded_process',side_effect=run):result=score_cpp(task,'```cpp\nint main(){}\n```','fixture')
        self.assertTrue(result['passed'])
        self.assertIn('--ulimit=cpu=10:10',commands[0])
        self.assertTrue(all('--ulimit=cpu=1:1' in command for command in commands[1:]))

    def test_v03_cli_reports_repair_types(self):
        with tempfile.TemporaryDirectory() as folder:
            predictions=Path(folder)/'empty.jsonl';predictions.write_text('')
            report=Path(folder)/'report.json'
            with patch('sys.argv',['axiombench','--suite',str(DATA/'tasks.jsonl.gz'),'grade','--predictions',str(predictions),'--output',str(report)]):
                with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(cli_main(),2)
            data=json.loads(report.read_text())
            self.assertEqual(data['cpp_repair_types']['syntax']['total'],10)
            self.assertEqual(data['cpp_repair_types']['semantic']['total'],15)
            self.assertIn('Синтаксис и ошибки компиляции',report.with_suffix('.html').read_text())


if __name__=='__main__':unittest.main()
