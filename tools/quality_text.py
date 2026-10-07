"""v0.3 balanced formal reasoning and new independently checkable families."""
import itertools
import math
from fractions import Fraction
from extended_text import general_families as old_general, math_families as old_math


def general_families(rng, variant):
    rows = old_general(rng, variant)
    # Shuffle which half asks the positive question; parity isn't a prompt feature.
    positive = variant in {0, 3, 4, 7, 9}
    names = rng.sample(['Ара', 'Бек', 'Вим', 'Гор', 'Дан', 'Ена'], 3)
    p, q, r = names
    replacements = {}
    def put(cat, prompt, answer, verifier, difficulty='intermediate'):
        replacements[cat] = (cat, difficulty, prompt, answer, verifier)
    relation = f'Все {q} являются {r}.' if positive else f'Ни один {q} не является {r}.'
    put('syllogism', f'Все {p} являются {q}. {relation} '
        f'Возможен ли объект, одновременно {p} и {r}? Ответ — boolean.', positive,
        'Finite set-model witness / exclusion')
    witness = q if positive else r
    put('existential_logic', f'Некоторые {p} являются {witness}. Все {q} являются {r}. '
        f'Обязательно ли некоторые {p} являются {q}? Ответ — boolean.', positive,
        'Existential witness or explicit countermodel')
    extra = f'Также: если горит {q}, включён {p}.' if positive else 'Других правил нет.'
    put('converse_fallacy', f'Если включён {p}, горит {q}. Горит {q}. {extra} '
        f'Обязательно ли включён {p}? Ответ — boolean.', positive, 'Enumerate propositional models')
    state = 'включён' if positive else 'выключен'
    put('contraposition', f'Если включён {p}, включён {q}. Сейчас {q} {state}. '
        f'Может ли {p} быть включён при выполнении правила? Ответ — boolean.', positive,
        'Satisfiability of implication and observation')
    claim = 'ложно' if positive else 'истинно'
    put('quantifier_negation', f'Утверждение «все {p} являются {q}» {claim}. '
        f'Обязательно ли существует {p}, не являющийся {q}? Ответ — boolean.', positive,
        'Finite model negation of universal quantifier')
    nodes = rng.sample(list('ABCDEFGH'), 6)
    edges = list(zip(nodes, nodes[1:]))
    if not positive: edges.append((nodes[-1], nodes[0]))
    rng.shuffle(edges)
    put('dependency_cycle', f'Все узлы {nodes} надо расположить. Ограничения «раньше»: {edges}. '
        'Возможен ли линейный порядок, выполняющий все ограничения? Ответ — boolean.', positive,
        'Enumerate all permutations')
    a, b = rng.sample(range(2, 30), 2)
    detail = f'Рост {q} больше роста {r} на {b} см.' if positive else f'Рост {q} больше роста {r}, но разница неизвестна.'
    put('insufficient_information', f'Рост {p} больше роста {r} на {a} см. {detail} '
        f'Можно ли однозначно определить, кто выше, {p} или {q}? Ответ — boolean.', positive,
        'Determine whether difference is fixed or admits opposite signs')
    start = rng.randint(-10, 10)
    end = start + rng.randint(3, 12)
    schedule = [('A', start, end)] + [(name, rng.randint(start-5,end+5), 0) for name in rng.sample(list('BCDEF'), 4)]
    schedule = [schedule[0]] + [(name, lo, lo+rng.randint(1,7)) for name,lo,_ in schedule[1:]]
    put('interval_conflict', f'События {schedule}. Интервалы полуоткрытые [start,end). '
        'Какие события пересекаются с A? Верни имена по алфавиту, A исключи.',
        sorted(name for name,lo,hi in schedule[1:] if lo < end and hi > start), 'Enumerate intersections')
    conclusion = 'Из одной связи доказано: зонты вызывают мокрую обувь.' if positive else 'Одна связь допускает влияние погоды; причинный эффект не установлен.'
    put('causal_inference', f'У {rng.randint(200,900)} жителей владение зонтом связано с мокрой обувью. '
        f'Нет рандомизации и данных о погоде. Оцени вывод: «{conclusion}» '
        'Согласуется ли этот вывод с ограничениями исследования? Ответ — boolean.', not positive,
        'Check causal identification claim, including its negation')
    winner = 'A' if positive else 'B'
    data = {winner: [(rng.randint(8,9),10),(rng.randint(6,7),10)],
            ('B' if winner=='A' else 'A'): [(rng.randint(4,5),10),(rng.randint(2,3),10)]}
    scale = rng.randint(2,9)
    displayed = {name:[(s*scale,n*scale) for s,n in pairs] for name,pairs in data.items()}
    put('simpson_groups', f'Успехи/все попытки в двух группах: {displayed}. '
        'Какая система имеет большую долю успеха в обеих группах по отдельности? Ответ — строка A или B.',
        winner, 'Compare exact rational rates within each stratum')
    rows = [replacements.get(row[0], row) for row in rows]

    # New families need several interacting steps, not just changed constants.
    variables = rng.sample(list('ABCDEFGH'), 6)
    implications = rng.sample([(a,b) for a in variables for b in variables if a!=b], 9)
    truths = rng.sample(variables, 2)
    closure = set(truths)
    while True:
        nxt = closure | {b for a,b in implications if a in closure}
        if nxt == closure: break
        closure = nxt
    rows.append(('implication_closure','advanced',f'Изначально истинны {truths}. '
        f'Правила {implications}: [X,Y] означает X⇒Y. Верни все переменные, '
        'истинность которых следует из фактов и правил, по алфавиту.',sorted(closure),'Enumerate all 64 boolean models'))
    people = rng.sample(['Ася','Боря','Вера','Глеб'],4)
    permutation = rng.sample(range(4),4)
    clues = [f'{people[i]} имеет номер {permutation[i]+1}' for i in range(4)]
    # Relative constraints fix the order, but the displayed relations are shuffled.
    order = sorted(people,key=lambda x:permutation[people.index(x)])
    relative = [(order[i],order[j],j-i) for i,j in [(0,2),(1,3),(0,1)]]
    rng.shuffle(relative)
    rows.append(('relative_positions','advanced',f'Четыре человека {people} стоят на позициях 1…4. '
        f'Ограничения {relative}: [X,Y,d] значит Y правее X ровно на d позиций. '
        'Верни единственный порядок слева направо.',order,'Enumerate 24 assignments'))
    programs = []
    value = rng.randint(-5,5)
    initial = value
    for _ in range(8):
        op = rng.choice(['add','mul','neg'])
        arg = rng.randint(-3,3)
        programs.append([op,arg] if op!='neg' else [op])
        value = value+arg if op=='add' else value*arg if op=='mul' else -value
    rows.append(('register_program','advanced',f'Регистр x={initial}. Команды {programs}. '
        'add a: x=x+a; mul a: x=x*a; neg: x=-x. Выполни последовательно. Верни итоговое целое.',value,'Independent expression fold'))
    universe = list(range(1,13))
    sets = {name:sorted(rng.sample(universe,rng.randint(3,8))) for name in ['A','B','C']}
    result = sorted((set(sets['A']) ^ set(sets['B'])) - set(sets['C']))
    rows.append(('set_composition','intermediate',f'Множества {sets}. Найди (A △ B) \\ C, '
        'где △ — симметрическая разность, \\ — разность множеств. Ответ — отсортированный массив.',result,'Membership truth table'))
    durations = {name:rng.randint(1,9) for name in list('ABCDE')}
    deps = [('A','C'),('B','C'),('B','D'),('C','E'),('D','E')]
    finish = {}
    for name in 'ABCDE': finish[name] = durations[name] + max([finish[a] for a,b in deps if b==name] or [0])
    rows.append(('parallel_schedule','advanced',f'Длительности задач {durations}; зависимости {deps} '
        'означают, что вторая начинается после завершения первой. Начало t=0, исполнителей неограниченно. '
        'Какое минимальное время завершения всех задач?',max(finish.values()),'Enumerate dependency path durations'))
    return rows


def math_families(rng, variant):
    rows = old_math(rng, variant)
    n = rng.randint(7,13)
    # Counts are generated by explicit enumeration, not a memorized named formula.
    length,target = 6+variant%3,variant+3
    count = sum(all(a!=b for a,b in zip(bits,bits[1:])) and sum(bits)==target
                for bits in itertools.product(range(3),repeat=length))
    rows.append(('ternary_constraints','advanced',f'Сколько строк длины {length} из цифр 0,1,2 имеют сумму цифр {target} '
        'и не имеют двух одинаковых соседних цифр?',str(count),'Enumerate 729 strings'))
    red,blue = rng.randint(3,8),rng.randint(3,8)
    # Draw four without replacement, condition on at least one red.
    answer = Fraction(math.comb(red,2)*math.comb(blue,2),math.comb(red+blue,4)-math.comb(blue,4))
    rows.append(('conditioned_urn','advanced',f'В урне {red} красных и {blue} синих шаров. '
        'Достали 4 без возвращения. Известно, что есть хотя бы один красный. '
        'Найди условную вероятность ровно двух красных.',str(answer),'Enumerate ordered samples independently'))
    cap = rng.randint(8,15)
    choices = [(rng.randint(1,6),rng.randint(2,12)) for _ in range(6)]
    answer = max(sum(choices[i][1] for i in range(6) if mask>>i&1)
                 for mask in range(64) if sum(choices[i][0] for i in range(6) if mask>>i&1)<=cap)
    rows.append(('discrete_optimization','advanced',f'Шесть предметов [вес,ценность]: {choices}. '
        f'Каждый можно взять один раз, вместимость {cap}. Найди максимальную суммарную ценность.',str(answer),'Exhaustive subsets / independent DP'))
    roots = rng.sample(range(-6,7),3)
    s1,s2,s3 = sum(roots),sum(a*b for a,b in itertools.combinations(roots,2)),math.prod(roots)
    answer = sum(x**4 for x in roots)
    rows.append(('quartic_newton','advanced',f'Корни x³-({s1})x²+({s2})x-({s3})=0 '
        'учитываются с кратностями. Найди сумму четвёртых степеней корней.',str(answer),'Explicit roots / independent Newton recurrence'))
    m = rng.randint(3,8)
    # Exactly one diagonal step in a grid path, remaining steps horizontal/vertical.
    answer = math.factorial(n+m-1)//(math.factorial(n-1)*math.factorial(m-1))
    rows.append(('grid_one_diagonal','advanced',f'Путь из (0,0) в ({n},{m}) использует шаги '
        '(1,0), (0,1), (1,1). Ровно один шаг должен быть (1,1). Сколько таких путей?',str(answer),'Multinomial / grid DP'))
    return rows
