import json
import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from axiombench.core import aggregate,digest,load_tasks,prompt_for,score_cpp,select_tasks

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'benchmarks/extended-v0.2'
TASKS=load_tasks(DATA/'tasks.jsonl.gz')


class ExtendedTests(unittest.TestCase):
    def test_counts_and_unique_prompts(self):
        self.assertEqual(Counter(t['track'] for t in TASKS),{'cpp':300,'general':300,'math':300})
        self.assertEqual(Counter(t.get('mode') for t in TASKS if t['track']=='cpp'),{'generation':150,'repair':150})
        self.assertEqual(len({prompt_for(t) for t in TASKS}),900)
        self.assertEqual(len({(t['family'],t.get('mode')) for t in TASKS}),90)

    def test_quick_samples_every_family_mode(self):
        short=select_tasks(TASKS,'all','quick')
        self.assertEqual(len(short),90)
        self.assertTrue(all(t['variant']==1 for t in short))
        self.assertEqual(len(select_tasks(TASKS,'math','full')),300)
        self.assertEqual(len(select_tasks(TASKS,'math','quick')),30)

    def test_checksums_and_no_duplicate_cases(self):
        manifest=json.loads((DATA/'manifest.json').read_text())
        for name,checksum in manifest['files'].items():self.assertEqual(digest(DATA/name),checksum)
        for task in TASKS:
            if task['track']=='cpp':
                self.assertGreaterEqual(len(task['tests']),20)
                # Repeated random cases are allowed only when expected output agrees.
                cases={}
                for case in task['tests']:
                    if case['stdin'] in cases:self.assertEqual(cases[case['stdin']],case['stdout'])
                    cases[case['stdin']]=case['stdout']

    def test_family_dependence_not_treated_as_iid(self):
        rows=[{'id':t['id'],'family':t['family'],'track':'math','passed':True,'status':'pass'} for t in TASKS if t['track']=='math']
        math=aggregate(rows)['math']
        self.assertEqual(math['family_count'],30)
        self.assertEqual(math['family_macro_accuracy_percent'],100)
        self.assertIsNone(math['wilson_95_percent'])

    def test_all_math_answers_independently(self):
        sys.path.insert(0,str(ROOT/'tools'))
        from verify_math import verify
        for task in TASKS:
            if task['track']=='math':verify(task)

    def test_compile_once_fresh_runtime_and_cleanup(self):
        task=next(t for t in TASKS if t['track']=='cpp')
        commands=[]
        def run(command,stdin,**kwargs):
            commands.append(command)
            if 'g++' in command:return 0,'','',None
            return 0,task['tests'][len(commands)-2]['stdout'],'',None
        with patch('axiombench.core.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')) as shell:
            with patch('axiombench.core.bounded_process',side_effect=run):score=score_cpp(task,'```cpp\nint main(){}\n```','sha256:fixture')
        self.assertTrue(score['passed'])
        self.assertEqual(sum('g++' in c for c in commands),1)
        names=[c[c.index('--name')+1] for c in commands]
        self.assertEqual(len(names),len(set(names)))
        self.assertTrue(any(c.args[0][:3]==['docker','volume','rm'] for c in shell.call_args_list))


if __name__=='__main__':unittest.main()
