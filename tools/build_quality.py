"""Build v0.3 without rewriting published v0.1/v0.2 datasets or generators."""
import gzip
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from quality_text import general_families, math_families
from quality_cpp import cpp_families, syntax_families

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'benchmarks'/'quality-v0.3'
SEED=2026100715


def common(task_id,track,category,difficulty,prompt,variant):
    return dict(id=task_id,track=track,kind='cpp' if track=='cpp' else 'json' if track=='general' else 'number',
                family=f'{track}-{category}',variant=variant+1,category=category,difficulty=difficulty,
                prompt=prompt,source='AxiomBench original synthetic public development task',
                license='MIT',split='dev',created_at='2026-10-07')


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'references').mkdir(exist_ok=True)
    (OUT/'fixtures').mkdir(exist_ok=True)
    rows=[];seen=set()
    for variant in range(10):
        for track,gen in [('general',general_families),('math',math_families)]:
            for family in range(35):
                for retry in range(101):
                    rng=random.Random(SEED+variant*100000+family*100+retry+(9000000 if track=='math' else 0))
                    category,difficulty,prompt,answer,verifier=gen(rng,variant)[family]
                    if (track,prompt) not in seen:break
                else:raise RuntimeError(f'Duplicate {track} {category} {variant}')
                seen.add((track,prompt))
                row=common(f'v03-{track}-{category}-v{variant+1:02}',track,category,difficulty,prompt,variant)
                row.update(answer=answer,verification_method=verifier)
                rows.append(row)
        algorithms=cpp_families(random.Random(SEED+20000000+variant),variant)
        syntax=syntax_families(random.Random(SEED+30000000+variant),variant)
        for data in algorithms+syntax:
            # Keep large case payloads once; dataset pins the compressed bytes.
            for case in data['tests']:
                if case.get('case_type')!='stress':continue
                for key in ('stdin','stdout'):
                    raw=case.pop(key).encode()
                    filename='fixtures/'+hashlib.sha256(raw).hexdigest()+'.txt.gz'
                    payload=gzip.compress(raw,mtime=0)
                    (OUT/filename).write_bytes(payload)
                    case[key+'_fixture']={'path':filename,'sha256':hashlib.sha256(payload).hexdigest()}
            reference=f"references/{data['category']}-v{variant+1:02}.cpp"
            (OUT/reference).write_text(data['reference_code'],encoding='utf-8')
            modes=['generation','repair'] if data['repair_type']=='semantic' else ['repair']
            for mode in modes:
                prompt=data['prompt']
                if mode=='repair' and data['repair_type']=='semantic':prompt='Исправь логическую ошибку в программе.\n'+prompt
                row=common(f"v03-cpp-{mode}-{data['category']}-v{variant+1:02}",'cpp',data['category'],data['difficulty'],prompt,variant)
                row.update(mode=mode,tests=data['tests'],reference=reference,
                           cpu_time_limit_seconds=data['cpu_time_limit_seconds'],
                           verification_method='Trusted C++ reference, independent oracle, negative solution checks')
                if mode=='repair':row.update(buggy_code=data['buggy_code'],repair_type=data['repair_type'])
                rows.append(row)
    rows.sort(key=lambda r:r['id'])
    from axiombench.core import prompt_for
    assert len({prompt_for(r) for r in rows})==len(rows)
    serialized=''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows).encode()
    (OUT/'tasks.jsonl.gz').write_bytes(gzip.compress(serialized,mtime=0))
    manifest=dict(name='AxiomBench Quality',version='0.3',seed=SEED,status='public-synthetic-development',license='MIT',
        created_at='2026-10-07',counts=dict(Counter(r['track'] for r in rows)),
        cpp_modes=dict(Counter(r['mode'] for r in rows if r['track']=='cpp')),
        repair_types=dict(Counter(r['repair_type'] for r in rows if r.get('mode')=='repair')),
        underlying_families=len({r['family'] for r in rows}),family_mode_groups=len({(r['family'],r.get('mode')) for r in rows}),
        cpp_test_cases=sum(len(r.get('tests',[])) for r in rows),
        stress_case_entries=sum(c.get('case_type')=='stress' for r in rows for c in r.get('tests',[])),
        warning='Public dependent parameter variants, not independent human-authored exam questions. No model calibration or private evaluation yet.',
        files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'})
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'},ensure_ascii=False,indent=2))


if __name__=='__main__':build()
