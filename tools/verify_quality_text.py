"""Independent checks from authored prompt text; never execute model answers."""
import ast
import itertools
import math
import re
from fractions import Fraction
from pathlib import Path
from axiombench.core import load_tasks
from verify_math import verify as verify_old_math

ROOT=Path(__file__).resolve().parents[1]


def literal(text,after):
    rest=text.split(after,1)[1]
    start=min(i for i in [rest.find('['),rest.find('{')] if i>=0)
    stack=[];quoted=None;escaped=False
    for end,ch in enumerate(rest[start:],start):
        if quoted:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch==quoted:quoted=None
        elif ch in "'\"":quoted=ch
        elif ch in '[{(':stack.append(ch)
        elif ch in ']})':
            stack.pop()
            if not stack:return ast.literal_eval(rest[start:end+1])
    raise ValueError('Unclosed literal')


def verify_new_math(task):
    p=task['prompt'];cat=task['category']
    if cat=='ternary_constraints':
        length,target=map(int,re.search(r'длины (\d+).*сумму цифр (\d+)',p).groups())
        states={(0,-1):1}
        for _ in range(length):
            nxt={}
            for (total,last),count in states.items():
                for digit in range(3):
                    if digit!=last:nxt[total+digit,digit]=nxt.get((total+digit,digit),0)+count
            states=nxt
        answer=sum(count for (total,last),count in states.items() if total==target)
    elif cat=='conditioned_urn':
        red,blue=map(int,re.search(r'(\d+) красных и (\d+) синих',p).groups())
        outcomes=list(itertools.combinations(range(red+blue),4))
        conditioned=[o for o in outcomes if any(x<red for x in o)]
        answer=Fraction(sum(sum(x<red for x in o)==2 for o in conditioned),len(conditioned))
    elif cat=='discrete_optimization':
        choices=literal(p,'предметов [вес,ценность]:')
        cap=int(re.search(r'вместимость (\d+)',p).group(1))
        dp=[0]*(cap+1)
        for w,v in choices:
            old=dp[:]
            for c in range(w,cap+1):dp[c]=max(old[c],old[c-w]+v)
        answer=dp[cap]
    elif cat=='quartic_newton':
        s1,s2,s3=map(int,re.search(r'x³-\((-?\d+)\)x²\+\((-?\d+)\)x-\((-?\d+)\)',p).groups())
        p1=s1;p2=s1*p1-2*s2;p3=s1*p2-s2*p1+3*s3
        answer=s1*p3-s2*p2+s3*p1
    elif cat=='grid_one_diagonal':
        n,m=map(int,re.search(r'в \((\d+),(\d+)\)',p).groups())
        dp={(0,0,0):1}
        for x in range(n+1):
            for y in range(m+1):
                for used in (0,1):
                    count=dp.get((x,y,used),0)
                    for xx,yy,uu in [(x+1,y,used),(x,y+1,used),(x+1,y+1,used+1)]:
                        if xx<=n and yy<=m and uu<=1:dp[xx,yy,uu]=dp.get((xx,yy,uu),0)+count
        answer=dp[n,m,1]
    else:
        verify_old_math(task);return
    assert Fraction(task['answer'])==answer,(task['id'],task['answer'],answer)


BALANCED={'syllogism','existential_logic','converse_fallacy','contraposition','quantifier_negation',
          'dependency_cycle','insufficient_information','interval_conflict','causal_inference','simpson_groups'}
NEW={'implication_closure','relative_positions','register_program','set_composition','parallel_schedule'}


def verify_general(task):
    p=task['prompt'];cat=task['category']
    if cat=='syllogism':
        # Possible nonempty type of an object satisfying the universal premises.
        allowed=[(a,b,c) for a,b,c in itertools.product([False,True],repeat=3)
                 if (not a or b) and ((not b or c) if 'Ни один' not in p else not(b and c))]
        answer=any(a and c for a,b,c in allowed)
    elif cat=='existential_logic':
        premise=re.search(r'Некоторые (\w+) являются (\w+)\. Все (\w+) являются (\w+)',p).groups()
        a,w,b,c=premise
        valid=[dict(zip([a,b,c],bits)) for bits in itertools.product([False,True],repeat=3)]
        witnesses=[s for s in valid if s[a] and s[w] and (not s[b] or s[c])]
        answer=all(s[b] for s in witnesses)
    elif cat=='converse_fallacy':
        states=[(a,b) for a,b in itertools.product([False,True],repeat=2)
                if b and (not a or b) and ('Также:' not in p or not b or a)]
        answer=all(a for a,b in states)
    elif cat=='contraposition':
        observed='выключен' not in p
        answer=any(a for a,b in itertools.product([False,True],repeat=2) if b==observed and (not a or b))
    elif cat=='quantifier_negation':
        # Enumerate finite universes of two objects, with possibly empty P.
        universes=list(itertools.product(list(itertools.product([False,True],repeat=2)),repeat=2))
        states=[u for u in universes if all(not a or b for a,b in u)==('истинно' in p)]
        answer=all(any(a and not b for a,b in u) for u in states)
    elif cat=='dependency_cycle':
        nodes=literal(p,'Все узлы');edges=literal(p,'«раньше»:')
        answer=any(all(order.index(a)<order.index(b) for a,b in edges) for order in itertools.permutations(nodes))
    elif cat=='insufficient_information':
        differences=list(map(int,re.findall(r'на (\d+) см',p)))
        # Enumerate a broad range of possible relative heights.
        a=differences[0]
        candidates=[differences[1]] if len(differences)==2 else range(1,max(100,a*2))
        answer=len({(a>b)-(a<b) for b in candidates})==1
    elif cat=='interval_conflict':
        schedule=literal(p,'События');_,start,end=schedule[0]
        answer=sorted(name for name,lo,hi in schedule[1:] if any(lo<=t<hi for t in range(start,end)))
    elif cat=='causal_inference':answer='не установлен' in p
    elif cat=='simpson_groups':
        data=literal(p,'группах:')
        answer=next(name for name in data if all(Fraction(*data[name][i])>Fraction(*data['B' if name=='A' else 'A'][i]) for i in range(2)))
    elif cat=='implication_closure':
        facts=literal(p,'истинны');rules=literal(p,'Правила')
        variables=sorted(set(facts)|{x for r in rules for x in r})
        models=[dict(zip(variables,bits)) for bits in itertools.product([False,True],repeat=len(variables))]
        models=[m for m in models if all(m[x] for x in facts) and all(not m[a] or m[b] for a,b in rules)]
        answer=[x for x in variables if all(m[x] for m in models)]
    elif cat=='relative_positions':
        people=literal(p,'человека');clues=literal(p,'Ограничения')
        orders=[list(o) for o in itertools.permutations(people) if all(o.index(b)-o.index(a)==d for a,b,d in clues)]
        assert len(orders)==1
        answer=orders[0]
    elif cat=='register_program':
        x=int(re.search(r'x=(-?\d+)',p).group(1));ops=literal(p,'Команды')
        # Compose affine transforms, then apply once to the initial register.
        a,b=1,0
        for op in ops:
            if op[0]=='add':b+=op[1]
            elif op[0]=='mul':a*=op[1];b*=op[1]
            else:a=-a;b=-b
        answer=a*x+b
    elif cat=='set_composition':
        data=literal(p,'Множества')
        answer=[x for x in sorted(set(sum(data.values(),[]))) if (x in data['A'])!=(x in data['B']) and x not in data['C']]
    elif cat=='parallel_schedule':
        durations=literal(p,'задач');edges=literal(p,'зависимости')
        paths=[[x] for x in durations]
        for _ in range(len(durations)):
            paths += [path+[b] for path in paths[:] for a,b in edges if path[-1]==a and b not in path]
        answer=max(sum(durations[x] for x in path) for path in paths)
    else:return False
    assert task['answer']==answer,(task['id'],task['answer'],answer)
    return True


def main():
    tasks=load_tasks(ROOT/'benchmarks/quality-v0.3/tasks.jsonl.gz')
    checked=0
    for task in tasks:
        if task['track']=='math':verify_new_math(task);checked+=1
        elif task['track']=='general':checked+=verify_general(task)
    print(f'Independent checks: {checked} tasks (350 math + 150 revised/new General)')


if __name__=='__main__':main()
