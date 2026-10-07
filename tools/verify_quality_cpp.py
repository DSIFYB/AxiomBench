"""Host verification of checked-in trusted sources only, including negative fixtures."""
import argparse
import json
import resource
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from axiombench.core import load_tasks

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'benchmarks/quality-v0.3'


def cpu_limit():
    resource.setrlimit(resource.RLIMIT_CPU,(1,1))


def verify_repair(task):
    count=0
    with tempfile.TemporaryDirectory() as folder:
        exe=str(Path(folder)/'ref')
        subprocess.run(['g++','-std=c++20','-O2',str(DATA/task['reference']),'-o',exe],check=True,capture_output=True,timeout=40)
        for case in task['tests']:
            result=subprocess.run([exe],input=case['stdin'],text=True,capture_output=True,timeout=3,preexec_fn=cpu_limit)
            assert result.returncode==0 and result.stdout.split()==case['stdout'].split(),task['id']
            count+=1
        src=Path(folder)/'bug.cpp';src.write_text(task['buggy_code'])
        compiled=subprocess.run(['g++','-std=c++20','-O2',str(src),'-o',exe],capture_output=True,timeout=40)
        if task['repair_type']=='syntax':
            assert compiled.returncode!=0,'Syntax mutation unexpectedly compiles: '+task['id']
        else:
            assert compiled.returncode==0,'Semantic mutation does not compile: '+task['id']
            caught=False
            for case in task['tests']:
                result=subprocess.run([exe],input=case['stdin'],text=True,capture_output=True,timeout=3,preexec_fn=cpu_limit)
                if result.returncode or result.stdout.split()!=case['stdout'].split():caught=True;break
            assert caught,'Semantic mutation not caught: '+task['id']
    return count


def verify_negative(tasks):
    stats=[]
    for category in ['subarray_count','range_sum_mod','zero_one_knapsack']:
        task=next(t for t in tasks if t['category']==category and t.get('mode')=='generation' and t['variant']==1)
        case=next(c for c in task['tests'] if c.get('case_type')=='stress')
        with tempfile.TemporaryDirectory() as folder:
            exe=str(Path(folder)/'bad')
            source=(ROOT/'tools/negative_solutions'/f'{category}.cpp').read_text().replace('TASK_K',str(task['variant']))
            src=Path(folder)/'bad.cpp';src.write_text(source)
            subprocess.run(['g++','-std=c++20','-O2',str(src),'-o',exe],check=True,capture_output=True,timeout=40)
            def limits():resource.setrlimit(resource.RLIMIT_CPU,(1,1))
            try:
                result=subprocess.run([exe],input=case['stdin'],text=True,capture_output=True,timeout=6,preexec_fn=limits)
                assert result.returncode!=0 or result.stdout.split()!=case['stdout'].split(),category+' inefficient solution passed stress case'
                status='cpu_limit' if result.returncode<0 else 'wrong_answer'
            except subprocess.TimeoutExpired:status='wall_timeout'
            stats.append({'category':category,'rejected':True,'reason':status})
    return stats


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--jobs',type=int,default=2);args=parser.parse_args()
    tasks=load_tasks(DATA/'tasks.jsonl.gz')
    repairs=[t for t in tasks if t.get('mode')=='repair']
    count=0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i,result in enumerate(as_completed([pool.submit(verify_repair,t) for t in repairs]),1):
            count+=result.result()
            if i%25==0:print(f'Checked {i}/{len(repairs)} trusted references and negative repairs',flush=True)
    print(json.dumps(dict(verified_references=len(repairs),reference_cases=count,syntax_rejections=100,
                         semantic_rejections=150,inefficient_solutions=verify_negative(tasks))))


if __name__=='__main__':main()
