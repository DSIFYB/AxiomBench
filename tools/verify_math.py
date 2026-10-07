"""Independent standard-library checks of all generated math answers.

Parses the fixed authored prompt grammar; no model strings are evaluated as code.
"""
import itertools
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from axiombench.core import load_tasks

ROOT=Path(__file__).resolve().parents[1]


def determinant(matrix):
    total=0
    for perm in itertools.permutations(range(len(matrix))):
        inversions=sum(perm[i]>perm[j] for i in range(len(perm)) for j in range(i+1,len(perm)))
        total+=(-1)**inversions*math.prod(matrix[i][perm[i]] for i in range(len(perm)))
    return total


def verify(task):
    nums=[int(s) for s in re.findall(r'-?\d+',task['prompt'])]
    cat=task['category']
    if cat=='rational_arithmetic':a,b,c,n=nums;answer=Fraction(a*n+c*b,b*n)
    elif cat=='linear_equation':a,b,c=nums;answer=Fraction(c-b,a)
    elif cat=='quadratic_vieta':b,c,_=nums;answer=b*b-2*c
    elif cat=='percent_change':price,pct,_=nums;answer=Fraction(price,100)*Fraction(100+pct,100)*(100-pct)
    elif cat=='arithmetic_sequence':a,b,n=nums;answer=sum(a+i*b for i in range(n))
    elif cat=='geometric_sequence':a,r,n=nums;answer=sum(a*r**i for i in range(n))
    elif cat=='gcd':a,b=nums;answer=max(d for d in range(1,min(a,b)+1) if a%d==0 and b%d==0)
    elif cat=='lcm':a,b=nums;answer=next(x for x in range(max(a,b),a*b+1,max(a,b)) if x%min(a,b)==0)
    elif cat=='modular_power':
        a,e,p=nums;answer=1
        for _ in range(e):answer=answer*a%p
    elif cat=='chinese_remainder':
        p,a,q,b=nums
        # Solve congruence through a modular inverse, not generator enumeration.
        answer=(a+p*((b-a)*pow(p,-1,q)%q))%(p*q)
    elif cat=='binomial':k,n=nums;answer=sum(1 for _ in itertools.combinations(range(n),k))
    elif cat=='binary_no_adjacent':
        n,=nums;answer=sum('11' not in format(x,f'0{n}b') for x in range(1<<n))
    elif cat=='derangements':
        n,=nums;answer=math.factorial(n)*sum((Fraction((-1)**i,math.factorial(i)) for i in range(n+1)),Fraction(0))
    elif cat=='dice_probability':_,n,target=nums;answer=Fraction(sum(x+y==target for x in range(1,n+1) for y in range(1,n+1)),n*n)
    elif cat=='hypergeometric':
        r,b,_,_=nums;sample=list(itertools.combinations(range(r+b),3));answer=Fraction(sum(sum(x<r for x in s)==2 for s in sample),len(sample))
    elif cat=='conditional_probability':
        _,n,divisor=nums;space=[x for x in range(1,n+1) if x%2==0];answer=Fraction(sum(x%divisor==0 for x in space),len(space))
    elif cat=='expectation':_,n=nums;answer=Fraction(sum(i*i for i in range(1,n+1)),n)
    elif cat=='bayes':
        _,n,_,_,_,_=nums;prior=Fraction(1,n);joint=prior*Fraction(3,4);answer=joint/(joint+(1-prior)*Fraction(1,5))
    elif cat=='triangle_inradius':a,b=nums;answer=Fraction(a+b-math.isqrt(a*a+b*b),2)
    elif cat=='rectangle_diagonal':a,b=nums;answer=math.isqrt(a*a+b*b)
    elif cat=='coordinate_area':
        points=list(zip(nums[::2],nums[1::2]));answer=Fraction(abs(sum(points[i][0]*points[(i+1)%3][1]-points[i][1]*points[(i+1)%3][0] for i in range(3))),2)
    elif cat=='derivative':
        a,b,c,_,x=nums
        # Symmetric finite-difference correction is exact for a cubic at h=1.
        f=lambda y:a*y**3+b*y**2+c*y+7
        answer=Fraction(f(x+1)-f(x-1),2)-a
    elif cat=='definite_integral':
        _,bound,a,b,c=nums
        # Simpson's rule is exact for quadratics.
        f=lambda x:a*x*x+b*x+c
        answer=Fraction(bound,6)*(f(0)+4*f(Fraction(bound,2))+f(bound))
    elif cat=='polynomial_limit':n=nums[0];answer=sum(1 for _ in range(n))
    elif cat=='determinant_2x2':answer=determinant([nums[:2],nums[2:]])
    elif cat=='determinant_3x3':answer=determinant([nums[:3],nums[3:6],nums[6:]])
    elif cat=='eigenvalue_trace':a,b,c,d=nums;answer=a+d
    elif cat=='linear_system':
        equations=re.search(r'x\+y=(-?\d+), 2x-y=(-?\d+)',task['prompt']);s,t=map(int,equations.groups());x=Fraction(s+t,3);answer=x*(s-x)
    elif cat=='newton_sums':
        a,b,c=nums;p1=-a;p2=-a*p1-2*b;answer=-a*p2-b*p1-3*c
    elif cat=='catalan':
        n,=nums;states={0:1}
        for _ in range(2*n):
            next_states={}
            for balance,count in states.items():
                if balance<n:next_states[balance+1]=next_states.get(balance+1,0)+count
                if balance>0:next_states[balance-1]=next_states.get(balance-1,0)+count
            states=next_states
        answer=states[0]
    else:raise AssertionError('Missing verifier: '+cat)
    assert Fraction(task['answer'])==answer,(task['id'],nums,answer,task['answer'])


if __name__=='__main__':
    tasks=[t for t in load_tasks(ROOT/'benchmarks/extended-v0.2/tasks.jsonl.gz') if t['track']=='math']
    for task in tasks:verify(task)
    print(f'Independently checked {len(tasks)} numeric math answers')
