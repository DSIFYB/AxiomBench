"""Build the reproducible 900-item public development suite."""
import hashlib
import gzip
import json
import random
from collections import Counter
from pathlib import Path
from extended_text import general_families, math_families
from extended_cpp import cpp_families

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'benchmarks'/'extended-v0.2'


def build():
    rows=[]
    seen=set()
    (OUT/'references').mkdir(parents=True,exist_ok=True)
    for variant in range(10):
        for track, generate in [('general',general_families),('math',math_families)]:
            for family in range(30):
                retry=0
                while True:
                    seed=20261007+variant*100000+family*100+retry+(0 if track=='general' else 9000000)
                    data=generate(random.Random(seed),variant)[family]
                    category,difficulty,prompt,answer,verifier=data
                    if (track,prompt) not in seen:break
                    retry+=1
                    if retry>100:raise RuntimeError(f'Duplicate prompt: {track} family {family} variant {variant}')
                seen.add((track,prompt))
                rows.append({'id':f'{track}-{family+1:02}-v{variant+1:02}','track':track,
                             'kind':'json' if track=='general' else 'number','family':f'{track}-{category}',
                             'variant':variant+1,'category':category,'difficulty':difficulty,
                             'prompt':prompt,'answer':answer,'verification_method':verifier,
                             'source':'AxiomBench original synthetic parameterized development task',
                             'license':'MIT','split':'dev','created_at':'2026-10-07'})
        for family,data in enumerate(cpp_families(random.Random(30261007+variant),variant),1):
            reference=f'references/cpp-{family:02}-v{variant+1:02}.cpp'
            (OUT/reference).write_text(data['reference_code'],encoding='utf-8')
            for mode in ('generation','repair'):
                prompt=data['prompt'] if mode=='generation' else 'Исправь ошибку в данной программе, сохранив требуемое поведение.\n'+data['prompt']
                assert ('cpp',prompt) not in seen
                seen.add(('cpp',prompt))
                task={'id':f'cpp-{mode}-{family:02}-v{variant+1:02}','track':'cpp','kind':'cpp',
                      'family':'cpp-'+data['category'],'variant':variant+1,'mode':mode,
                      'category':data['category'],'difficulty':data['difficulty'],'prompt':prompt,
                      'tests':data['tests'],'reference':reference,
                      'verification_method':'Independent Python oracle; trusted C++ reference; repair mutation must fail',
                      'source':'AxiomBench original synthetic parameterized development task',
                      'license':'MIT','split':'dev','created_at':'2026-10-07'}
                if mode=='repair':task['buggy_code']=data['buggy_code']
                rows.append(task)
    rows.sort(key=lambda r:r['id'])
    serialized=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows).encode('utf-8')
    (OUT/'tasks.jsonl.gz').write_bytes(gzip.compress(serialized,mtime=0))
    manifest={'name':'AxiomBench Extended','version':'0.2','seed':20261007,'status':'public-synthetic-development',
              'license':'MIT','created_at':'2026-10-07','counts':dict(Counter(r['track'] for r in rows)),
              'cpp_modes':dict(Counter(r['mode'] for r in rows if r['track']=='cpp')),
              'underlying_families':len({r['family'] for r in rows}),
              'family_mode_groups':len({(r['family'],r.get('mode')) for r in rows}),
              'cpp_test_cases':sum(len(r.get('tests',[])) for r in rows),
              'warning':'10 dependent parameter variants per family/mode, not 900 independent human-authored problems. No official external dataset is bundled.',
              'files':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in ('manifest.json','tasks.jsonl')}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'},ensure_ascii=False,indent=2))


if __name__=='__main__':build()
