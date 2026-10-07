"""v0.3 maximum-size stress inputs and genuine compilation-error repair."""
from bisect import bisect_left
from collections import deque
from extended_cpp import cpp_families as old_cpp


def cpp_families(rng, variant):
    rows = old_cpp(rng, variant)
    k = variant+1
    by_name = {r['category']:r for r in rows}
    def add(name, inp, out):
        by_name[name]['tests'].append({'stdin':inp,'stdout':out,'case_type':'stress'})
    n = 100000
    periodic = [((i*17+k*3)%101)-50 for i in range(n)]
    array_input = str(n)+'\n'+' '.join(map(str,periodic))+'\n'
    add('weighted_sum', array_input, str(sum((x-k)*k for x in periodic))+'\n')
    mod = 97+10*k
    # Large q as well as n rejects per-query scans of the array.
    qs = [(1,n-i%101) for i in range(n)]
    prefix=[0]
    for x in periodic:prefix.append(prefix[-1]+x)
    add('range_sum_mod',f'{n} {n}\n'+' '.join(map(str,periodic))+'\n'+
        ''.join(f'{l} {r}\n' for l,r in qs), ''.join(f'{(prefix[r]-prefix[l-1])%mod}\n' for l,r in qs))
    target = k-5
    # Alternating values: closed-form pair counting, independent of hashmap reference.
    alternating = [target,0]*(n//2) if target else [0]*n
    ans = 4*(n//2)-2 if target else n*(n+1)//2
    add('subarray_count',f'{n}\n'+' '.join(map(str,alternating))+'\n',str(ans)+'\n')
    window=k+1
    add('sliding_max',array_input,' '.join(str(max(periodic[i:i+window])) for i in range(n-window+1))+'\n')
    sorted_values = [i//3-16000 for i in range(n)]
    x=12000+k
    add('lower_bound',f'{n} {x}\n'+' '.join(map(str,sorted_values))+'\n',str(bisect_left(sorted_values,x)+k)+'\n')
    step=k+2
    intervals = [((i//5)*step,(i//5)*step) for i in range(n)]
    merged = intervals[::5]
    # Reverse sorted input prevents accidentally relying on input order.
    add('interval_merge',f'{n}\n'+''.join(f'{l} {r}\n' for l,r in reversed(intervals)),
        f'{len(merged)}\n'+''.join(f'{l} {r}\n' for l,r in merged))
    add('bracket_types','('*50000+')'*50000+'\n','YES\n')
    # Independent maximum-subarray oracle using running min of prefix sums.
    cur=0;low=0;best=-10**30
    for x in periodic:
        cur+=x-k;best=max(best,cur-low);low=min(low,cur)
    add('maximum_subarray',array_input,str(best)+'\n')
    # A long chain bypasses the forbidden vertex; no small fixed graph shortcut.
    nodes=[i for i in range(n) if i!=k]
    edges=list(zip(nodes,nodes[1:]))
    add('bfs_forbidden',f'{n} {len(edges)}\n'+''.join(f'{a} {b}\n' for a,b in edges)+
        f'{nodes[0]} {nodes[-1]}\n',str(len(nodes)-1)+'\n')
    # Long cheap chain + expensive hub edges makes repeated relaxation costly.
    size=20000
    edges=[(i,i+1,1) for i in range(size-1)]+[(0,i,10**9) for i in range(2,size)]
    add('dijkstra_fee',f'{size} {len(edges)}\n'+''.join(f'{a} {b} {w}\n' for a,b,w in reversed(edges))+
        f'0 {size-1}\n',str((size-1)*(k+1))+'\n')
    edges=[(i,i+1,k) for i in range(n-1)]
    add('dsu_color',f'{n} {len(edges)}\n'+''.join(f'{a} {b} {c}\n' for a,b,c in edges)+
        f'{n}\n'+' '.join(map(str,range(n)))+'\n',('100000 '*n).rstrip()+'\n')
    length=1000
    add('gap_subsequence',f'{length}\n'+' '.join(str(i*k) for i in range(length))+'\n',str(length)+'\n')
    add('edit_cost','a'*200+'\n'+'b'*200+'\n','200\n')
    add('edit_cost','\n'+'a'*200+'\n',str(200*k)+'\n')
    add('modular_product','1000000000000000000 999999999999999999 1000000000000000000\n',str(k)+'\n')
    add('zero_one_knapsack','200 2000\n'+''.join(f'10 {1000000-i}\n' for i in range(200)),
        str(sum(1000000-i+k for i in range(200)))+'\n')
    for row in rows:
        row['repair_type']='semantic'
        row['cpu_time_limit_seconds']=1
    return rows


def syntax_families(rng, variant):
    k=variant+1
    arrays=[[],[0],[-1,0,1],[10**9]*8,[-10**9]*8]+[
        [rng.randint(-100,100) for _ in range(rng.randint(0,30))] for _ in range(15)]
    tests=[{'stdin':f'{len(a)}\n'+' '.join(map(str,a))+'\n',
            'stdout':str(sum(x*k for x in a))+'\n'} for a in arrays]
    # Readable functions put the faults in different language constructs.
    source=f'''#include <iostream>
#include <vector>
using namespace std;

long long weighted(const vector<long long>& a) {{
    long long total = 0;
    for (long long value : a) {{
        total += value * {k};
    }}
    return total;
}}

int main() {{
    int n;
    cin >> n;
    vector<long long> values(n);
    for (auto& value : values) {{
        cin >> value;
    }}
    cout << weighted(values) << "\\n";
    return 0;
}}
'''
    changes=[
        ('missing_semicolon','long long total = 0;','long long total = 0','basic'),
        ('missing_brace','    return total;\n}','    return total;','basic'),
        ('missing_parenthesis','weighted(values)','weighted(values','basic'),
        ('template_bracket','vector<long long> values','vector<long long values','intermediate'),
        ('undeclared_identifier','total += value','total += valye','basic'),
        ('missing_header','#include <vector>\n','','intermediate'),
        ('missing_namespace','using namespace std;\n','','basic'),
        ('invalid_stream_operator','cin >> n;','cin >< n;','basic'),
        ('invalid_return_type','long long weighted','long long long weighted','intermediate'),
        ('invalid_reference_declaration','auto& value','auto&&& value','intermediate'),
    ]
    out=[]
    for name,before,after,difficulty in changes:
        assert before in source
        out.append(dict(category='syntax_'+name,difficulty=difficulty,
            prompt=f'Программа должна прочитать n (0≤n≤100000) и n целых |a_i|≤10^9, '
                f'затем вывести сумму a_i*{k}. Пустая сумма равна 0. Найди и исправь ошибку '
                'синтаксиса или компиляции, сохранив требуемое поведение. Верни полный исправленный исходник.',
            reference_code=source,buggy_code=source.replace(before,after,1),tests=tests,
            repair_type='syntax',cpu_time_limit_seconds=1))
    return out
