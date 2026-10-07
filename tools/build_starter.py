"""Deterministically build the original public development set; no downloaded tasks."""
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "starter-v0.1"
rows = []


def add(task_id, track, category, difficulty, prompt, answer=None, **extra):
    row = {"id": task_id, "track": track, "kind": "cpp" if track == "cpp" else ("number" if track == "math" else "json"),
           "category": category, "difficulty": difficulty, "prompt": prompt,
           "source": "AxiomBench original development task", "license": "MIT", "split": "dev",
           "created_at": "2026-10-07", **extra}
    if track != "cpp":
        row["answer"] = answer
    rows.append(row)


general = [
    ("logic", "basic", "Все зеты — ломы. Ни один лом не является тиром. Может ли какой-нибудь зет быть тиром? Ответ: JSON boolean.", False),
    ("logic", "intermediate", "Некоторые раны — кеты. Все кеты — моры. Следует ли из этого, что некоторые раны — моры? Ответ: JSON boolean.", True),
    ("causality", "intermediate", "В наблюдении продавцы зонтов чаще получают промокшую обувь. Доказывает ли только эта корреляция, что продажа зонтов вызывает промокание обуви? Ответ: JSON boolean.", False),
    ("state_tracking", "basic", "В ящике лежит красный жетон. Его переложили в сумку, сумку в шкаф, затем жетон вынули из сумки и положили на стол. Где жетон? Ответ: строка из вариантов ящик, сумка, шкаф, стол.", "стол"),
    ("planning", "intermediate", "Нужно выполнить A, B, C, D. B требует A; C требует A; D требует B и C. Выбери лексикографически наименьший допустимый порядок. Ответ: массив букв.", ["A", "B", "C", "D"]),
    ("data_interpretation", "intermediate", "Доли успеха: система A — 30/40 в лёгкой группе и 2/10 в сложной; система B — 8/10 в лёгкой и 12/40 в сложной. Какая система успешнее в обеих группах по отдельности? Ответ: строка A или B.", "B"),
    ("constraint_solving", "intermediate", "Аня, Борис и Вера сидят в ряд. Аня не слева и не справа. Борис слева от Веры. Перечисли имена слева направо. Ответ: массив строк.", ["Борис", "Аня", "Вера"]),
    ("rule_induction", "intermediate", "Преобразование слова: abcd→dabc, 12345→51234. Примените то же правило к wxyz. Ответ: строка.", "zwxy"),
    ("instruction_following", "basic", "В строке 'лук; мак; лук; дуб; мак' сохрани только первые появления слов, затем отсортируй их по русскому алфавиту. Ответ: массив строк.", ["дуб", "лук", "мак"]),
    ("uncertainty", "intermediate", "Олег выше Иры. Саша выше Иры. Можно ли однозначно определить, кто выше: Олег или Саша? Ответ: JSON boolean.", False),
    ("context_reasoning", "intermediate", "В вымышленном календаре после понедельника идут среда, вторник, четверг, пятница, суббота, воскресенье, и цикл повторяется. Сегодня среда. Какой день будет через 3 дня? Ответ: строка в именительном падеже.", "пятница"),
    ("formal_reasoning", "advanced", "Устройства P,Q,R могут быть включены или выключены. Ровно два включены. Если P включено, Q выключено. Если R выключено, Q включено. Перечисли включённые устройства по алфавиту, если P включено. Ответ: массив строк.", ["P", "R"]),
]
for i, (category, difficulty, prompt, answer) in enumerate(general, 1):
    add(f"general-{i:03}", "general", category, difficulty, prompt, answer)

math = [
    ("arithmetic", "basic", "Вычисли 7/12 + 5/18 в виде несократимой дроби.", "31/36"),
    ("algebra", "basic", "Найди x из уравнения 7x - 9 = 40.", "7"),
    ("combinatorics", "intermediate", "Сколько пятисимвольных двоичных строк не содержат двух соседних единиц?", "13"),
    ("probability", "intermediate", "Два независимых честных шестигранных кубика бросают один раз. Какова вероятность суммы 9?", "1/9"),
    ("number_theory", "intermediate", "Найди остаток 7^123 при делении на 13.", "5"),
    ("geometry", "intermediate", "Прямоугольный треугольник имеет катеты 9 и 12. Найди радиус вписанной окружности.", "3"),
    ("calculus", "intermediate", "Вычисли определённый интеграл от 0 до 2 функции 3x^2 - 2x + 1.", "6"),
    ("linear_algebra", "intermediate", "Вычисли определитель матрицы [[2,1,0],[0,3,1],[1,0,4]].", "25"),
    ("combinatorics", "advanced", "Сколько перестановок чисел 1,2,3,4,5 не оставляют ни одного числа на исходном месте?", "44"),
    ("probability", "advanced", "В урне 4 красных и 3 синих шара. Без возвращения вытаскивают 3 шара. Найди вероятность ровно 2 красных шаров.", "18/35"),
    ("number_theory", "advanced", "Найди наименьшее положительное x, удовлетворяющее x≡2 (mod 5), x≡3 (mod 7), x≡4 (mod 9).", "157"),
    ("algebra", "advanced", "Вычисли сумму кубов всех комплексных корней многочлена x^3 - 2x^2 + 3x - 4 с учётом кратностей.", "2"),
]
for i, (category, difficulty, prompt, answer) in enumerate(math, 1):
    add(f"math-{i:03}", "math", category, difficulty, prompt, answer)

header = "#include <bits/stdc++.h>\nusing namespace std;\n"
cpp = [
    ("sum", "generation", "basic", "Прочитай n (0≤n≤100000), затем n целых чисел |a_i|≤10^9. Выведи их сумму. Используй тип, исключающий переполнение при этих ограничениях.",
     "int main(){int n;cin>>n;long long s=0,x;while(n--){cin>>x;s+=x;}cout<<s<<'\\n';}", None,
     [("0\n", "0\n"), ("3\n1 -2 4\n", "3\n"), ("3\n1000000000 1000000000 1000000000\n", "3000000000\n"), ("2\n-9 -7\n", "-16\n")]),
    ("prefix_sum", "generation", "intermediate", "Прочитай n,q (1≤n≤100000, 1≤q≤100000), массив n чисел |a_i|≤10^9, затем q запросов l,r с 1≤l≤r≤n. Для каждого запроса выведи сумму a_l…a_r. Требуется O(n+q).",
     "int main(){int n,q;cin>>n>>q;vector<long long>p(n+1);for(int i=1;i<=n;i++){long long x;cin>>x;p[i]=p[i-1]+x;}while(q--){int l,r;cin>>l>>r;cout<<p[r]-p[l-1]<<'\\n';}}", None,
     [("4 3\n1 -2 3 4\n1 4\n2 3\n4 4\n", "6\n1\n4\n"), ("1 1\n-7\n1 1\n", "-7\n"), ("3 1\n1000000000 1000000000 1000000000\n1 3\n", "3000000000\n"), ("2 2\n0 0\n1 1\n1 2\n", "0\n0\n")]),
    ("brackets", "generation", "intermediate", "Прочитай одну строку длиной 1…100000 из символов (,),[,],{,}. Выведи YES, если скобки правильно вложены и согласованы по типу; иначе NO. Требуется O(n).",
     "int main(){string s,t;cin>>s;for(char c:s){if(c=='('||c=='['||c=='{')t+=c;else{if(t.empty()){cout<<\"NO\\n\";return 0;}char b=t.back();t.pop_back();if(!((b=='('&&c==')')||(b=='['&&c==']')||(b=='{'&&c=='}'))){cout<<\"NO\\n\";return 0;}}}cout<<(t.empty()?\"YES\\n\":\"NO\\n\");}", None,
     [("([]{})\n", "YES\n"), ("([)]\n", "NO\n"), (")\n", "NO\n"), ("((\n", "NO\n"), ("{}[]()\n", "YES\n")]),
    ("shortest_path", "generation", "intermediate", "Прочитай n,m (1≤n≤100000, 0≤m≤200000), затем m рёбер неориентированного невзвешенного графа, затем s,t. Вершины нумеруются с 1. Выведи минимальное число рёбер пути s→t или -1, если пути нет. Допускаются петли и повторные рёбра. Требуется O(n+m).",
     "int main(){int n,m;cin>>n>>m;vector<vector<int>>g(n+1);while(m--){int a,b;cin>>a>>b;g[a].push_back(b);g[b].push_back(a);}int s,t;cin>>s>>t;vector<int>d(n+1,-1);queue<int>q;d[s]=0;q.push(s);while(!q.empty()){int v=q.front();q.pop();for(int u:g[v])if(d[u]<0){d[u]=d[v]+1;q.push(u);}}cout<<d[t]<<'\\n';}", None,
     [("4 3\n1 2\n2 3\n3 4\n1 4\n", "3\n"), ("3 1\n1 2\n1 3\n", "-1\n"), ("1 0\n1 1\n", "0\n"), ("4 4\n1 2\n2 4\n1 3\n3 4\n1 4\n", "2\n")]),
    ("overflow", "repair", "basic", "Исправь программу: она читает n (0≤n≤100000) и n чисел |a_i|≤10^9, должна вывести сумму, но переполняется. Верни полную исправленную программу.",
     "int main(){int n;cin>>n;long long s=0,x;while(n--){cin>>x;s+=x;}cout<<s<<'\\n';}",
     "int main(){int n;cin>>n;int s=0,x;while(n--){cin>>x;s+=x;}cout<<s<<'\\n';}",
     [("0\n", "0\n"), ("3\n1000000000 1000000000 1000000000\n", "3000000000\n"), ("3\n-1000000000 -1000000000 -1000000000\n", "-3000000000\n"), ("3\n1 2 3\n", "6\n")]),
    ("binary_search", "repair", "intermediate", "Исправь поиск первого индекса i (нумерация с 0), для которого a_i≥x в отсортированном массиве. Если такого элемента нет, выведи n. Ввод: n,x (0≤n≤100000), затем n чисел. Для пустого массива ответ 0. Требуется O(log n) после чтения.",
     "int main(){int n,x;cin>>n>>x;vector<int>a(n);for(int &v:a)cin>>v;int l=0,r=n;while(l<r){int m=l+(r-l)/2;if(a[m]<x)l=m+1;else r=m;}cout<<l<<'\\n';}",
     "int main(){int n,x;cin>>n>>x;vector<int>a(n);for(int &v:a)cin>>v;int l=0,r=n-1;while(l<r){int m=(l+r)/2;if(a[m]<=x)l=m+1;else r=m;}cout<<l<<'\\n';}",
     [("0 5\n", "0\n"), ("4 2\n1 2 2 5\n", "1\n"), ("3 9\n1 2 3\n", "3\n"), ("3 0\n1 2 3\n", "0\n"), ("1 7\n7\n", "0\n")]),
    ("negative_values", "repair", "intermediate", "Исправь алгоритм максимальной суммы непустого непрерывного подмассива. Ввод n (1≤n≤100000), затем n чисел |a_i|≤10^9. Для массива из отрицательных чисел нельзя выбирать пустой подмассив. Требуется O(n).",
     "int main(){int n;cin>>n;long long x;cin>>x;long long best=x,cur=x;for(int i=1;i<n;i++){cin>>x;cur=max(x,cur+x);best=max(best,cur);}cout<<best<<'\\n';}",
     "int main(){int n;cin>>n;long long best=0,cur=0,x;while(n--){cin>>x;cur=max(0LL,cur+x);best=max(best,cur);}cout<<best<<'\\n';}",
     [("3\n-4 -2 -7\n", "-2\n"), ("1\n-9\n", "-9\n"), ("5\n2 -1 3 -9 7\n", "7\n"), ("3\n1000000000 1000000000 1000000000\n", "3000000000\n")]),
    ("modular_multiplication", "repair", "advanced", "Исправь переполнение в вычислении (a*b) mod m. Ввод: a,b,m, где 0≤a,b≤10^18, 1≤m≤10^18. Можно использовать __int128 в GCC C++20. Выведи целый остаток.",
     "int main(){long long a,b,m;cin>>a>>b>>m;cout<<(long long)((__int128)a*b%m)<<'\\n';}",
     "int main(){long long a,b,m;cin>>a>>b>>m;cout<<(a*b)%m<<'\\n';}",
     [("1000000000000000000 1000000000000000000 999999999999999999\n", "1\n"), ("0 999999999999999999 7\n", "0\n"), ("123 456 1\n", "0\n"), ("12 13 17\n", "3\n")]),
]
for i, (category, mode, difficulty, prompt, reference, buggy, tests) in enumerate(cpp, 1):
    task_id = f"cpp-{i:03}"
    extra = {"mode": mode, "tests": [{"stdin": inp, "stdout": out} for inp, out in tests],
             "reference": f"references/{task_id}.cpp"}
    if buggy:
        extra["buggy_code"] = header + buggy
    add(task_id, "cpp", category, difficulty, prompt, **extra)
    (OUT / "references").mkdir(parents=True, exist_ok=True)
    (OUT / "references" / f"{task_id}.cpp").write_text(header + reference + "\n", encoding="utf-8")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tasks.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
manifest = {"name": "AxiomBench Starter", "version": "0.1", "status": "public-development-only",
            "created_at": "2026-10-07", "license": "MIT", "source": "original AxiomBench development tasks",
            "counts": {"general": 12, "cpp_generation": 4, "cpp_repair": 4, "math": 12, "cpp_test_cases": 34},
            "files": {str(f.relative_to(OUT)): hashlib.sha256(f.read_bytes()).hexdigest()
                      for f in sorted(OUT.rglob('*')) if f.is_file() and f.name != 'manifest.json'}}
(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Built {len(rows)} original development tasks")
