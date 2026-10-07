"""Paired family-cluster bootstrap for two complete, compatible local reports."""
import random
from collections import defaultdict
from .core import overall_score


def compare_reports(a,b,resamples=2000):
    if resamples<100:raise ValueError('Use at least 100 bootstrap resamples')
    for key in ['suite_sha256','profile','axiombench_version','docker_image_id']:
        if a.get(key)!=b.get(key):raise ValueError('Incompatible reports: '+key)
    for report in (a,b):
        if not overall_score(report['tasks'])['comparable']:raise ValueError('Comparison requires complete results for all four dimensions')
        if not report.get('run_metadata'):raise ValueError('Comparison requires recorded run metadata')
    for key in ['selected_ids_sha256','temperature','max_tokens']:
        if key not in a['run_metadata'] or key not in b['run_metadata']:raise ValueError('Missing run setting: '+key)
        if a['run_metadata'].get(key)!=b['run_metadata'].get(key):raise ValueError('Incompatible run setting: '+key)
    left={r['id']:r for r in a['tasks']};right={r['id']:r for r in b['tasks']}
    if len(left)!=len(a['tasks']) or len(right)!=len(b['tasks']) or left.keys()!=right.keys():
        raise ValueError('Task IDs differ or contain duplicates')
    dimensions=defaultdict(lambda:defaultdict(list))
    for task_id,row in left.items():
        other=right[task_id]
        for key in ('track','mode','family','repair_type'):
            if row.get(key)!=other.get(key):raise ValueError('Task metadata mismatch: '+task_id)
        dimension=row['track'] if row['track']!='cpp' else 'cpp_'+row['mode']
        dimensions[dimension][row.get('family',task_id)].append(int(row['passed'])-int(other['passed']))
    # Resample paired families together; parameter variants are not IID items.
    rates={dimension:{family:sum(families[family])/len(families[family]) for family in sorted(families)}
           for dimension,families in dimensions.items()}
    # Equal variants per family required: otherwise bootstrap and task score differ.
    for families in dimensions.values():
        if len({len(values) for values in families.values()})!=1:
            raise ValueError('Cluster comparison requires equal variant counts within each dimension')
    rng=random.Random(20261007)
    # Shared C++ generation/repair families get the SAME draw, preserving dependence.
    cpp=defaultdict(list)
    for family in sorted(rates['cpp_generation'].keys() | rates['cpp_repair'].keys()):
        present=tuple(mode for mode in ('cpp_generation','cpp_repair') if family in rates[mode])
        cpp[present].append(family)
    def draw():
        scores=[sum(rng.choices(list(rates[key].values()),k=len(rates[key])))/len(rates[key])
                for key in ('general','math')]
        sums=dict(cpp_generation=0,cpp_repair=0)
        for present,families in cpp.items():
            sampled=rng.choices(families,k=len(families))
            for mode in present:sums[mode]+=sum(rates[mode][family] for family in sampled)
        return 25*(sum(scores)+sum(sums[mode]/len(rates[mode]) for mode in sums))
    samples=sorted(draw() for _ in range(resamples))
    delta=25*sum(sum(group.values())/len(group) for group in rates.values())
    low,high=samples[int(.025*resamples)],samples[min(resamples-1,int(.975*resamples))]
    return dict(model_a=a['run_metadata']['model'],model_b=b['run_metadata']['model'],
                delta_a_minus_b=round(delta,2),family_bootstrap_95=[round(low,2),round(high,2)],
                interval_excludes_zero=low>0 or high<0,resamples=resamples,
                note='Exploratory paired family bootstrap for this public suite; not proof of general superiority or run-to-run stability.')
