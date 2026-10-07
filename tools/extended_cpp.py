"""Fifteen executable C++ families, each in generation and seeded-bug repair mode."""
import heapq
from collections import deque

HEADER = '#include <bits/stdc++.h>\nusing namespace std;\n'


def cpp_families(rng, variant):
    k = variant + 1
    families = []
    def add(name, difficulty, prompt, body, mutation, cases):
        before, after = mutation
        assert before in body, name
        buggy = body.replace(before, after, 1)
        families.append({"category": name, "difficulty": difficulty, "prompt": prompt,
                         "reference_code": HEADER+body+'\n', "buggy_code": HEADER+buggy+'\n',
                         "tests": [{"stdin": inp, "stdout": out} for inp,out in cases]})

    arrays = [[],[0],[1,-1],[10**9]*8,[-10**9]*8,[-9,-7,-2]] + [[rng.randint(-100,100) for _ in range(rng.randint(1,35))] for _ in range(18)]
    arrays += [[10**9]*10000]
    cases = [(f'{len(a)}\n'+ ' '.join(map(str,a))+'\n',str(sum((x-k)*k for x in a))+'\n') for a in arrays]
    add('weighted_sum','basic',f'Прочитай n (0≤n≤100000) и n целых |a_i|≤10^9. Выведи сумму (a_i-{k})*{k}. Пустая сумма равна 0. Исключи переполнение.',
        f'int main(){{int n;cin>>n;long long s=0,x;while(n--){{cin>>x;s+=(x-{k})*{k};}}cout<<s<<"\\n";}}',('long long s=0,x','int s=0,x'),cases)

    mod = 97 + 10*k
    cases=[]
    for a in arrays[1:]:
        queries=[(0,len(a)-1),(0,0),(len(a)-1,len(a)-1)] + [tuple(sorted([rng.randrange(len(a)),rng.randrange(len(a))])) for _ in range(4)]
        inp=f'{len(a)} {len(queries)}\n'+' '.join(map(str,a))+'\n'+''.join(f'{l+1} {r+1}\n' for l,r in queries)
        cases.append((inp,''.join(str(sum(a[l:r+1])%mod)+'\n' for l,r in queries)))
    add('range_sum_mod','intermediate',f'Ввод: n,q (1≤n,q≤100000), n целых |a_i|≤10^9, затем q запросов l,r (1≤l≤r≤n). Для каждого выведи сумму от l до r по модулю {mod}, остаток в 0…{mod-1}. Требуется O(n+q).',
        f'int main(){{int n,q;cin>>n>>q;vector<long long>p(n+1);for(int i=1;i<=n;i++){{long long x;cin>>x;p[i]=p[i-1]+x;}}while(q--){{int l,r;cin>>l>>r;long long v=(p[r]-p[l-1])%{mod};if(v<0)v+={mod};cout<<v<<"\\n";}}}}',('if(v<0)v+=','if(v>0)v+='),cases)

    target=k-5
    subarrays=[[target],[0,0,0],[target,0,0],[-1,1,target],[2,-2,2,-2]] + [[rng.randint(-8,8) for _ in range(rng.randint(1,25))] for _ in range(18)]
    cases=[]
    for a in subarrays:
        ans=sum(sum(a[l:r])==target for l in range(len(a)) for r in range(l+1,len(a)+1))
        cases.append((f'{len(a)}\n'+' '.join(map(str,a))+'\n',str(ans)+'\n'))
    add('subarray_count','intermediate',f'Ввод: n (1≤n≤100000), затем n чисел |a_i|≤10^9. Посчитай непустые непрерывные подмассивы с суммой {target}. Требуется ожидаемое O(n).',
        f'int main(){{int n;cin>>n;unordered_map<long long,long long>f;f[0]=1;long long p=0,ans=0,x;while(n--){{cin>>x;p+=x;ans+=f[p-({target})];f[p]++;}}cout<<ans<<"\\n";}}',('f[0]=1','f[0]=0'),cases)

    window=k+1
    ws=[list(range(30,0,-1)),[-10]*30,list(range(30)),[5]*(window+2)] + [[rng.randint(-100,100) for _ in range(rng.randint(window,40))] for _ in range(18)]
    cases=[(f'{len(a)}\n'+' '.join(map(str,a))+'\n',' '.join(str(max(a[i:i+window])) for i in range(len(a)-window+1))+'\n') for a in ws]
    add('sliding_max','intermediate',f'Ввод: n ({window}≤n≤100000) и n целых |a_i|≤10^9. Выведи максимумы всех последовательных окон длины {window} слева направо. Требуется O(n).',
        f'int main(){{int n;cin>>n;vector<long long>a(n);deque<int>d;for(int i=0;i<n;i++){{cin>>a[i];while(!d.empty()&&d.front()<=i-{window})d.pop_front();while(!d.empty()&&a[d.back()]<=a[i])d.pop_back();d.push_back(i);if(i>={window}-1)cout<<a[d.front()]<<" ";}}cout<<"\\n";}}',('d.front()<=i-','d.front()<i-'),cases)

    cases=[]
    for a in [[],[7],[1,2,2,5],[-5,-5,-5],list(range(40))]+[sorted(rng.randint(-8,8) for _ in range(20)) for _ in range(18)]:
        for x in ([0,7] if not a else [a[0],a[-1],a[-1]+1]):
            ans=next((i for i,v in enumerate(a) if v>=x),len(a))+k
            cases.append((f'{len(a)} {x}\n'+' '.join(map(str,a))+'\n',str(ans)+'\n'))
    add('lower_bound','intermediate',f'Ввод: n,x (0≤n≤100000), отсортированный массив n целых в диапазоне [-10^9,10^9]. Найди первый нулевой индекс i с a_i≥x, либо i=n. Выведи i+{k}. После чтения требуется O(log n).',
        f'int main(){{int n;long long x;cin>>n>>x;vector<long long>a(n);for(auto &v:a)cin>>v;int l=0,r=n;while(l<r){{int m=l+(r-l)/2;if(a[m]<x)l=m+1;else r=m;}}cout<<l+{k}<<"\\n";}}',('a[m]<x','a[m]<=x'),cases)

    def merge(intervals):
        out=[]
        for l,r in sorted(intervals):
            if out and l<=out[-1][1]+k:
                out[-1][1]=max(out[-1][1],r)
            else:out.append([l,r])
        return out
    sets=[[],[(0,1),(1+k,3+k)],[(1,9),(2,3)],[(0,0),(k+1,k+1)]] + [[tuple(sorted((rng.randint(-30,30),rng.randint(-30,30)))) for _ in range(15)] for _ in range(18)]
    cases=[]
    for intervals in sets:
        out=merge(intervals)
        cases.append((str(len(intervals))+'\n'+''.join(f'{l} {r}\n' for l,r in intervals),str(len(out))+'\n'+''.join(f'{l} {r}\n' for l,r in out)))
    add('interval_merge','intermediate',f'Ввод: n (0≤n≤100000), затем n закрытых интервалов l,r с -10^9≤l≤r≤10^9. Сортируй по l,r; объединяй следующий с последним результатом, если его l≤последнее r+{k}. Выведи число результатов, затем l,r каждой пары. Пустой ввод даёт 0. Требуется O(n log n).',
        f'int main(){{int n;cin>>n;vector<pair<long long,long long>>a(n),o;for(auto &p:a)cin>>p.first>>p.second;sort(a.begin(),a.end());for(auto p:a){{if(!o.empty()&&p.first<=o.back().second+{k})o.back().second=max(o.back().second,p.second);else o.push_back(p);}}cout<<o.size()<<"\\n";for(auto p:o)cout<<p.first<<" "<<p.second<<"\\n";}}',('p.first<=o.back()','p.first<o.back()'),cases)

    marker='@#$%&*+=!? '[variant]
    def brackets(s):
        stack=[]
        for ch in s:
            if ch==marker:continue
            if ch in '([{<':stack.append(ch)
            elif not stack or '([{<'.index(stack.pop())!=')]}>' .index(ch):return False
        return not stack
    strings=['','([)]','([]{})','<[]>','(((',')',marker*4,'('+marker+')','<'+marker+'>']
    strings += [''.join(rng.choice('()[]{}<>'+marker) for _ in range(20)) for _ in range(18)]
    cases=[(s+'\n',('YES' if brackets(s) else 'NO')+'\n') for s in strings]
    add('bracket_types','intermediate',f'Прочитай одну строку (может быть пустой), длина≤100000, символы ()[]{{}}<> и {marker!r}. Игнорируй символ {marker!r}. Проверь правильную вложенность четырёх типов скобок. Выведи YES или NO. Требуется O(n).',
        f'int main(){{string s,t,op="([{{<",cl=")]}}>";getline(cin,s);for(char c:s){{if(c==\'{marker}\')continue;auto i=op.find(c);if(i!=string::npos)t+=c;else{{auto j=cl.find(c);if(t.empty()||op.find(t.back())!=j){{cout<<"NO\\n";return 0;}}t.pop_back();}}}}cout<<(t.empty()?"YES\\n":"NO\\n");}}',('t.empty()||op.find(t.back())!=j','t.empty()'),cases)

    cases=[]
    for a in arrays[1:]:
        transformed=[x-k for x in a]
        if len(a)>100:
            ans=sum(transformed) # all 10^9, explicitly positive
        else:ans=max(sum(transformed[l:r]) for l in range(len(a)) for r in range(l+1,len(a)+1))
        cases.append((f'{len(a)}\n'+' '.join(map(str,a))+'\n',str(ans)+'\n'))
    add('maximum_subarray','intermediate',f'Ввод: n (1≤n≤100000), n целых |a_i|≤10^9. Замени каждое число на a_i-{k}; найди максимальную сумму непустого непрерывного подмассива. Требуется O(n).',
        f'int main(){{int n;cin>>n;long long x;cin>>x;x-={k};long long cur=x,best=x;for(int i=1;i<n;i++){{cin>>x;x-={k};cur=max(x,cur+x);best=max(best,cur);}}cout<<best<<"\\n";}}',('long long cur=x,best=x','long long cur=0,best=0'),cases)

    forbidden=k
    def distance(n,edges,s,t):
        if s==forbidden or t==forbidden:return -1
        graph=[[] for _ in range(n)]
        for a,b in edges:
            if forbidden not in (a,b):graph[a].append(b);graph[b].append(a)
        d=[-1]*n;d[s]=0;queue=deque([s])
        while queue:
            v=queue.popleft()
            for u in graph[v]:
                if d[u]<0:d[u]=d[v]+1;queue.append(u)
        return d[t]
    graphs=[(12,[],0,11),(12,[(0,forbidden),(forbidden,11)],0,11),(12,[(0,11)],0,11),(12,[],0,0),(12,[],forbidden,forbidden)]
    graphs += [(12,[(rng.randrange(12),rng.randrange(12)) for _ in range(20)],*rng.sample(range(12),2)) for _ in range(18)]
    cases=[(f'{n} {len(e)}\n'+''.join(f'{a} {b}\n' for a,b in e)+f'{s} {t}\n',str(distance(n,e,s,t))+'\n') for n,e,s,t in graphs]
    add('bfs_forbidden','intermediate',f'Ввод: n,m (12≤n≤100000, 0≤m≤200000), m рёбер неориентированного графа 0…n-1, затем s,t. Вершина {forbidden} запрещена, включая s/t. Выведи минимальное число рёбер пути без неё; иначе -1. Петли и повторные рёбра допустимы. Требуется O(n+m).',
        f'int main(){{int n,m;cin>>n>>m;vector<vector<int>>g(n);while(m--){{int a,b;cin>>a>>b;if(a!={forbidden}&&b!={forbidden}){{g[a].push_back(b);g[b].push_back(a);}}}}int s,t;cin>>s>>t;if(s=={forbidden}||t=={forbidden}){{cout<<-1<<"\\n";return 0;}}vector<int>d(n,-1);queue<int>q;d[s]=0;q.push(s);while(!q.empty()){{int v=q.front();q.pop();for(int u:g[v])if(d[u]<0){{d[u]=d[v]+1;q.push(u);}}}}cout<<d[t]<<"\\n";}}',('cout<<d[t]','cout<<max(0,d[t])'),cases)

    def shortest(n,edges,s,t):
        inf=10**30;d=[inf]*n;d[s]=0
        for _ in range(n):
            old=d[:]
            for a,b,w in edges:d[b]=min(d[b],old[a]+w+k);d[a]=min(d[a],old[b]+w+k)
        return -1 if d[t]==inf else d[t]
    graphs=[(4,[(0,1,10**9),(1,2,10**9),(2,3,10**9)],0,3),(3,[],0,2),(2,[(0,1,0)],0,1),(2,[],0,0)]
    graphs += [(8,[(rng.randrange(8),rng.randrange(8),rng.randint(0,50)) for _ in range(20)],*rng.sample(range(8),2)) for _ in range(18)]
    cases=[(f'{n} {len(e)}\n'+''.join(f'{a} {b} {w}\n' for a,b,w in e)+f'{s} {t}\n',str(shortest(n,e,s,t))+'\n') for n,e,s,t in graphs]
    add('dijkstra_fee','advanced',f'Ввод: n,m (1≤n≤20000, 0≤m≤100000), m неориентированных рёбер u,v,w (вершины 0…n-1, 0≤w≤10^9), затем s,t. Стоимость прохода каждого ребра w+{k}. Выведи минимальную стоимость, либо -1. Требуется O((n+m)log n).',
        f'int main(){{int n,m;cin>>n>>m;vector<vector<pair<int,long long>>>g(n);while(m--){{int a,b;long long w;cin>>a>>b>>w;g[a].push_back({{b,w+{k}}});g[b].push_back({{a,w+{k}}});}}int s,t;cin>>s>>t;vector<long long>d(n,LLONG_MAX/4);priority_queue<pair<long long,int>,vector<pair<long long,int>>,greater<pair<long long,int>>>q;d[s]=0;q.push({{0,s}});while(!q.empty()){{auto [dv,v]=q.top();q.pop();if(dv!=d[v])continue;for(auto [u,w]:g[v])if(d[u]>dv+w){{d[u]=dv+w;q.push({{d[u],u}});}}}}cout<<(d[t]==LLONG_MAX/4?-1:d[t])<<"\\n";}}',('cout<<(d[t]==LLONG_MAX/4?-1:d[t])','cout<<(d[t]==LLONG_MAX/4?-1:(int)d[t])'),cases)

    def component_sizes(n,edges,queries):
        graph=[[] for _ in range(n)]
        for a,b,color in edges:
            if color==k:graph[a].append(b);graph[b].append(a)
        answers=[]
        for q in queries:
            seen={q};todo=[q]
            while todo:
                for u in graph[todo.pop()]:
                    if u not in seen:seen.add(u);todo.append(u)
            answers.append(len(seen))
        return answers
    graphs=[(4,[(0,1,k),(2,3,k),(0,2,k)],[0,1,2,3]),(3,[],[0,2]),(3,[(0,1,k%10+1)],[0,1])]
    graphs += [(15,[(rng.randrange(15),rng.randrange(15),rng.choice([k,k%10+1])) for _ in range(25)],list(range(15))) for _ in range(18)]
    cases=[(f'{n} {len(e)}\n'+''.join(f'{a} {b} {c}\n' for a,b,c in e)+str(len(q))+'\n'+' '.join(map(str,q))+'\n',' '.join(map(str,component_sizes(n,e,q)))+'\n') for n,e,q in graphs]
    add('dsu_color','intermediate',f'Ввод: n,m (1≤n≤100000, 0≤m≤200000), m рёбер u,v,c (0≤u,v<n, 1≤c≤10), затем q (1≤q≤100000) и q вершин. Используй только рёбра цвета {k}. Для каждой запрошенной вершины выведи размер её компоненты. Требуется DSU с амортизированной почти линейной сложностью.',
        f'int main(){{int n,m;cin>>n>>m;vector<int>p(n),sz(n,1);iota(p.begin(),p.end(),0);auto find=[&](int x){{while(p[x]!=x){{p[x]=p[p[x]];x=p[x];}}return x;}};while(m--){{int a,b,c;cin>>a>>b>>c;if(c!={k})continue;a=find(a);b=find(b);if(a!=b){{if(sz[a]<sz[b])swap(a,b);p[b]=a;sz[a]+=sz[b];}}}}int q;cin>>q;while(q--){{int x;cin>>x;cout<<sz[find(x)]<<" ";}}cout<<"\\n";}}',('sz[a]+=sz[b]','sz[a]++'),cases)

    sequences=[[],[0,k,2*k,3*k],[4,4,4],[10,0,-10]]+[[rng.randint(-20,20) for _ in range(rng.randint(1,12))] for _ in range(18)]
    def subsequence(a):
        # Exhaustive masks, independent of reference's quadratic DP.
        best=0
        for mask in range(1<<len(a)):
            s=[a[i] for i in range(len(a)) if mask>>i&1]
            if all(y-x>=k for x,y in zip(s,s[1:])):best=max(best,len(s))
        return best
    cases=[(str(len(a))+'\n'+' '.join(map(str,a))+'\n',str(subsequence(a))+'\n') for a in sequences]
    add('gap_subsequence','intermediate',f'Ввод: n (0≤n≤1000), n целых |a_i|≤10^9. Найди максимальную длину подпоследовательности (порядок сохраняется), в которой каждый следующий элемент не меньше предыдущего+{k}. Пустой массив даёт 0. Допускается O(n²).',
        f'int main(){{int n;cin>>n;vector<long long>a(n);for(auto &x:a)cin>>x;vector<int>d(n,1);int ans=0;for(int i=0;i<n;i++){{for(int j=0;j<i;j++)if(a[i]-a[j]>={k})d[i]=max(d[i],d[j]+1);ans=max(ans,d[i]);}}cout<<ans<<"\\n";}}',('a[i]-a[j]>=','a[i]-a[j]>'),cases)

    pairs=[('','abc'),('abc',''),('abc','abc'),('ab','ba'),('a','b')]+[(''.join(rng.choice('abc') for _ in range(rng.randint(0,8))),''.join(rng.choice('abc') for _ in range(rng.randint(0,8)))) for _ in range(18)]
    def edit(a,b):
        # Dijkstra over prefix-coordinate graph instead of matrix recurrence.
        todo=[(0,0,0)];dist={(0,0):0}
        while todo:
            cost,i,j=heapq.heappop(todo)
            if cost!=dist[i,j]:continue
            if (i,j)==(len(a),len(b)):return cost
            edges=[]
            if i<len(a):edges.append((i+1,j,k))
            if j<len(b):edges.append((i,j+1,k))
            if i<len(a) and j<len(b):edges.append((i+1,j+1,int(a[i]!=b[j])))
            for ii,jj,w in edges:
                if cost+w<dist.get((ii,jj),10**9):dist[ii,jj]=cost+w;heapq.heappush(todo,(cost+w,ii,jj))
    cases=[(a+'\n'+b+'\n',str(edit(a,b))+'\n') for a,b in pairs]
    add('edit_cost','advanced',f'Прочитай две строки отдельными строками (каждая может быть пустой), длина≤200, буквы a…z. Стоимость вставки и удаления равна {k}, замены — 1, совпадения — 0. Выведи минимальную стоимость преобразования первой строки во вторую. Допускается O(|a||b|).',
        f'int main(){{string a,b;getline(cin,a);getline(cin,b);int n=a.size(),m=b.size();vector<vector<int>>d(n+1,vector<int>(m+1));for(int i=0;i<=n;i++)d[i][0]=i*{k};for(int j=0;j<=m;j++)d[0][j]=j*{k};for(int i=1;i<=n;i++)for(int j=1;j<=m;j++)d[i][j]=min({{d[i-1][j]+{k},d[i][j-1]+{k},d[i-1][j-1]+(a[i-1]!=b[j-1])}});cout<<d[n][m]<<"\\n";}}',('d[0][j]=j*','d[0][j]=0*'),cases)

    triples=[(10**18,10**18,10**18-1),(0,10**18,7),(123,456,1),(12,13,17)]+[(rng.randrange(10**18),rng.randrange(10**18),rng.randrange(1,10**18)) for _ in range(18)]
    cases=[(f'{a} {b} {m}\n',str((a*b+k)%m)+'\n') for a,b,m in triples]
    add('modular_product','advanced',f'Ввод: a,b,m (0≤a,b≤10^18, 1≤m≤10^18). Вычисли (a*b+{k}) mod m без переполнения. Допускается GCC __int128.',
        f'int main(){{long long a,b,m;cin>>a>>b>>m;cout<<(long long)(((__int128)a*b+{k})%m)<<"\\n";}}',('(__int128)a*b','a*b'),cases)

    items=[([(1,3)],4),([],5),([(5,2)],4),([(1,2),(2,3),(3,8)],5)] + [([(rng.randint(1,8),rng.randint(0,20)) for _ in range(rng.randint(1,9))],rng.randint(0,20)) for _ in range(18)]
    cases=[]
    for a,cap in items:
        best=0
        for mask in range(1<<len(a)):
            chosen=[a[i] for i in range(len(a)) if mask>>i&1]
            if sum(w for w,v in chosen)<=cap:best=max(best,sum(v+k for w,v in chosen))
        inp=f'{len(a)} {cap}\n'+''.join(f'{w} {v}\n' for w,v in a)
        cases.append((inp,str(best)+'\n'))
    add('zero_one_knapsack','advanced',f'Ввод: n,W (0≤n≤200, 0≤W≤2000), n пар вес,ценность (1≤вес≤2000, 0≤ценность≤10^6). Каждый предмет можно брать не более одного раза. Его полезность равна ценность+{k}. Максимизируй суммарную полезность при весе≤W; пустой набор разрешён. Выведи максимум. Требуется O(nW).',
        f'int main(){{int n,W;cin>>n>>W;vector<long long>d(W+1);while(n--){{int w,v;cin>>w>>v;for(int j=W;j>=w;j--)d[j]=max(d[j],d[j-w]+v+{k});}}cout<<d[W]<<"\\n";}}',('for(int j=W;j>=w;j--)','for(int j=w;j<=W;j++)'),cases)
    assert len(families)==15
    return families
