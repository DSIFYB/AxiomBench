"""Verify trusted repository references only; never evaluate model code here."""
import argparse
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from axiombench.core import load_tasks

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'benchmarks'/'extended-v0.2'


def verify_pair(pair):
    generation,repair=pair
    count=0
    with tempfile.TemporaryDirectory() as folder:
        exe=str(Path(folder)/'reference')
        subprocess.run(['g++','-std=c++20','-O2',str(DATA/generation['reference']),'-o',exe],check=True,timeout=40,capture_output=True)
        for case in generation['tests']:
            p=subprocess.run([exe],input=case['stdin'],text=True,capture_output=True,timeout=3)
            if p.returncode or p.stdout.split()!=case['stdout'].split():
                raise AssertionError(f"Reference mismatch: {generation['id']}: {case['stdin'][:80]} -> {p.stdout[:80]} != {case['stdout'][:80]}")
            count+=1
        path=Path(folder)/'bug.cpp';path.write_text(repair['buggy_code'],encoding='utf-8')
        subprocess.run(['g++','-std=c++20','-O2',str(path),'-o',exe],check=True,timeout=40,capture_output=True)
        caught=False
        for case in repair['tests']:
            p=subprocess.run([exe],input=case['stdin'],text=True,capture_output=True,timeout=3)
            if p.returncode or p.stdout.split()!=case['stdout'].split():caught=True;break
        if not caught:raise AssertionError('Uncaught mutation: '+repair['id'])
    return count


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--jobs',type=int,default=2);args=parser.parse_args()
    tasks=load_tasks(DATA/'tasks.jsonl.gz')
    cpp={t['id']:t for t in tasks if t['track']=='cpp'}
    pairs=[(t,cpp[t['id'].replace('generation','repair')]) for t in cpp.values() if t['mode']=='generation']
    count=0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i,result in enumerate(as_completed([pool.submit(verify_pair,pair) for pair in pairs]),1):
            count+=result.result()
            if i%15==0:print(f'Verified {i}/{len(pairs)} reference/mutation pairs',flush=True)
    print(json.dumps({'verified_references':len(pairs),'reference_test_cases':count,'caught_repair_variants':len(pairs)}))


if __name__=='__main__':main()
