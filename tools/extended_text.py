"""Thirty reasoning and thirty mathematics families with deterministic variants.

These are original synthetic public development tasks, not imported official items.
"""
import itertools
import math
from collections import deque
from fractions import Fraction


def graph_distance(edges, source, target):
    queue = deque([(source, 0)])
    seen = {source}
    while queue:
        node, depth = queue.popleft()
        if node == target:
            return depth
        for a, b in edges:
            if a == node and b not in seen:
                seen.add(b)
                queue.append((b, depth + 1))
    return -1


def general_families(rng, variant):
    n = variant + 3
    names = ["Ара", "Бек", "Вим", "Гор", "Дан"]
    rng.shuffle(names)
    p, q, r = names[:3]
    result = []
    def add(category, difficulty, prompt, answer, verifier):
        result.append((category, difficulty, prompt, answer, verifier))

    add("syllogism", "basic", f"Все {p} являются {q}. Ни один {q} не является {r}. Возможен ли объект, одновременно {p} и {r}? Ответ — boolean.", False, "Universal-set disjointness")
    add("existential_logic", "intermediate", f"Некоторые {p} являются {q}. Все {q} являются {r}. Обязательно ли некоторые {p} являются {r}? Ответ — boolean.", True, "Existential witness propagates through subset")
    add("converse_fallacy", "intermediate", f"Если включён датчик {p}, горит лампа {q}. Лампа {q} горит. Обязательно ли включён датчик {p}? Других правил нет. Ответ — boolean.", False, "Counterexample: lamp can have another cause")
    add("contraposition", "intermediate", f"Если включён {p}, включён {q}. Сейчас {q} выключен. Может ли {p} быть включён при выполнении правила? Ответ — boolean.", False, "Truth-table implication")
    add("quantifier_negation", "intermediate", f"Утверждение «все {p} являются {q}» ложно. Следует ли, что существует {p}, не являющийся {q}? Ответ — boolean.", True, "Negation of universal quantifier")
    values = [rng.randint(-20, 20) for _ in range(n)]
    cutoff = rng.randint(-5, 5)
    answer = sorted(set(x for x in values if x > cutoff))
    add("filter_sort", "basic", f"Дан массив {values}. Оставь числа строго больше {cutoff}, удали повторы, отсортируй по возрастанию. Ответ — массив целых.", answer, "Direct set/filter/sort")
    sequence = [rng.choice(names) for _ in range(n + 4)]
    add("stable_dedup", "basic", f"В списке {sequence} оставь первые появления каждого имени; порядок сохрани. Ответ — массив строк.", list(dict.fromkeys(sequence)), "First occurrence traversal")
    mapping = dict(zip(names, rng.sample(range(1, 100), len(names))))
    add("lookup_join", "basic", f"Коды имён: {mapping}. Запросы: {sequence[:5]}. Верни коды в порядке запросов, сохрани повторы. Ответ — массив целых.", [mapping[x] for x in sequence[:5]], "Dictionary join")
    threshold = rng.randint(2, 4)
    votes = [rng.randint(0, 9) for _ in range(7)]
    add("counting_constraints", "basic", f"Баллы: {votes}. Посчитай, сколько баллов не меньше {threshold} и при этом чётные. Ответ — целое число.", sum(x >= threshold and x % 2 == 0 for x in votes), "Conjunction of predicates")
    locations = ["ящик", "сумка", "шкаф", "стол"]
    rng.shuffle(locations)
    add("object_tracking", "basic", f"Жетон был в {locations[0]}. Его переложили в {locations[1]}, затем в {locations[2]}, после этого в {locations[3]}. Затем переставили пустой {locations[0]}. Где жетон? Ответ — одно слово.", locations[3], "Last move affecting the object")
    initial = rng.randint(0, 20)
    operations = [rng.randint(-4, 4) for _ in range(6)]
    add("state_updates", "basic", f"Начальное значение счётчика {initial}. Последовательно прибавили числа {operations}. Затем прочитали счётчик без изменения. Ответ — конечное целое значение.", initial + sum(operations), "Sequential additive updates")
    switches = [rng.randrange(1, 5) for _ in range(n)]
    add("toggle_parity", "intermediate", f"Лампы 1,2,3,4 сначала выключены. Переключения в порядке: {switches}; каждое меняет состояние указанной лампы. Верни номера включённых ламп по возрастанию.", [i for i in range(1, 5) if switches.count(i) % 2], "Parity of occurrence counts")
    ops = [("push", rng.randint(0, 9)) for _ in range(3)] + [("pop", None), ("push", n), ("pop", None)]
    add("stack_simulation", "intermediate", f"Пустой стек. Команды: push {ops[0][1]}, push {ops[1][1]}, push {ops[2][1]}, pop, push {n}, pop. Верни содержимое снизу вверх.", [ops[0][1], ops[1][1]], "Stack LIFO simulation")
    queue = rng.sample(range(10, 50), 4)
    add("queue_simulation", "intermediate", f"В пустую очередь добавили {queue[0]}, {queue[1]}, {queue[2]}; извлекли один элемент; добавили {queue[3]}; извлекли один элемент. Верни очередь от начала к концу.", queue[2:], "Queue FIFO simulation")
    nodes = ["A", "B", "C", "D", "E"]
    order = rng.sample(nodes, 5)
    edges = list(zip(order, order[1:])) + [(order[0], order[3])]
    add("topological_order", "intermediate", f"Зависимости {edges}: пара [X,Y] означает, что X нужно выполнить раньше Y. Выполни все A,B,C,D,E. Верни допустимый порядок (он единственный).", order, "Complete dependency chain fixes order")
    edges2 = [(a, b) for a in range(5) for b in range(5) if a != b and rng.random() < .25]
    start, goal = rng.sample(range(5), 2)
    add("graph_distance", "intermediate", f"Ориентированный граф вершин 0…4 с рёбрами {edges2}. Минимальное число рёбер от {start} до {goal}? Если пути нет, ответ -1.", graph_distance(edges2, start, goal), "BFS and Floyd-Warshall cross-check")
    add("graph_reachability", "intermediate", f"Ориентированный граф 0…4, рёбра {edges2}. Можно ли попасть из {goal} в {start}? Ответ — boolean.", graph_distance(edges2, goal, start) >= 0, "BFS reachability")
    precedence = list(zip(order, order[1:])) + [(order[-1], order[0])]
    add("dependency_cycle", "intermediate", f"Обязательные отношения «раньше»: {precedence}. Возможно ли расположить A,B,C,D,E в линейном порядке, выполнив все отношения? Ответ — boolean.", False, "Directed cycle precludes topological order")
    permutations = list(itertools.permutations(names[:4]))
    chosen = rng.choice(permutations)
    clues = [(chosen[i], chosen[i + 1]) for i in range(3)]
    add("ordering_puzzle", "intermediate", f"Четыре человека {names[:4]} стоят в ряд. Каждый из следующих людей стоит левее второго в паре: {clues}. Верни порядок слева направо.", list(chosen), "Enumerate all 24 permutations")
    a, b = rng.sample(range(1, 20), 2)
    add("insufficient_information", "intermediate", f"Рост {p} больше роста {r} на {a} см; рост {q} тоже больше роста {r}, но разница неизвестна. Можно ли определить, кто выше: {p} или {q}? Ответ — boolean.", False, "Construct two opposite consistent assignments")
    direction = rng.choice([-1, 1])
    word = "".join(rng.sample("abcdefghijk", 6))
    transform = lambda s: s[-1:] + s[:-1] if direction == 1 else s[1:] + s[:1]
    add("rotation_rule", "intermediate", f"Правило: abcd→{transform('abcd')}, 12345→{transform('12345')}. Примени то же правило к {word}. Ответ — строка.", transform(word), "Fixed one-position rotation")
    shift = rng.randrange(1, 10)
    digits = "".join(str(rng.randrange(10)) for _ in range(6))
    result_digits = "".join(str((int(x) + shift) % 10) for x in digits)
    add("digit_rule", "intermediate", f"Каждую цифру независимо заменяют на (цифра+{shift}) mod 10. Преобразуй строку {digits}, сохрани длину и ведущие нули. Ответ — строка.", result_digits, "Per-character modular addition")
    bits = [rng.choice([True, False]) for _ in range(4)]
    answer = (bits[0] and not bits[1]) or (bits[2] != bits[3])
    add("boolean_expression", "intermediate", f"A,B,C,D={bits}. Вычисли (A AND NOT B) OR (C XOR D). Ответ — boolean.", answer, "Truth table")
    count = rng.randrange(1, n+1)
    choices = [x for x in itertools.product([False, True], repeat=n) if sum(x) == count and not (x[0] and x[1])]
    add("boolean_model_count", "advanced", f"Есть {n} выключателей с номерами 1…{n}. Ровно {count} включены, 1 и 2 не могут быть включены одновременно. Сколько существует допустимых состояний? Ответ — целое.", len(choices), "Exhaustive finite boolean-state enumeration")
    dataset = [(x, rng.randint(1, 9)) for x in names[:4]]
    add("tie_breaking", "basic", f"Баллы участников {dataset}. Отсортируй имена: сначала балл по убыванию, при равенстве имя по возрастанию Unicode. Ответ — массив имён.", [x for x, _ in sorted(dataset, key=lambda x: (-x[1], x[0]))], "Explicit secondary sorting key")
    schedule = [("A", 0, n), ("B", n-1, n+2), ("C", n, n+3), ("D", n+3, n+6)]
    add("interval_conflict", "intermediate", f"События {schedule}, запись [имя,start,end]. Интервалы полуоткрытые [start,end). Какие события пересекаются с A? Верни имена по алфавиту, само A исключи.", [name for name, lo, hi in schedule[1:] if max(0, lo) < min(n, hi)], "Intersection length is positive")
    add("causal_inference", "intermediate", f"В выборке из {n*100} жителей владение зонтом связано с мокрой обувью. Нет случайного распределения зонтов и данных о погоде. Доказывает ли только эта связь, что зонты вызывают мокрую обувь? Ответ — boolean.", False, "Correlation alone permits confounding")
    sens = rng.choice([70, 80, 90])
    add("base_rate", "advanced", f"В популяции {n*1000} объектов ровно {n*10} дефектных. Тест находит {sens}% дефектных и ошибочно отмечает 10% остальных. Все доли здесь дают целые количества. Сколько здоровых объектов получат ложноположительный результат? Ответ — целое.", n*99, "False positives use non-defective base, not all objects")
    add("simpson_groups", "intermediate", f"Успехи A: {3*n}/{4*n} в лёгкой группе, {2*n}/{10*n} в сложной. B: {8*n}/{10*n} в лёгкой, {3*n}/{10*n} в сложной. Какая система имеет большую долю успеха в обеих группах по отдельности? Ответ — строка A или B.", "B", "Compare rates within each stratum")
    code = rng.choice(["0012", "0007", "0100", "0093"]) + str(variant)
    add("instruction_literal", "basic", f"Верни ровно строку кода {code}. Не преобразуй её в число: ведущие нули значимы.", code, "Literal string identity")
    assert len(result) == 30
    return result


def math_families(rng, variant):
    result = []
    def add(category, difficulty, prompt, answer, verifier):
        result.append((category, difficulty, prompt, str(answer), verifier))
    n = variant + 4
    a, b, c = [rng.randint(2, 15) for _ in range(3)]
    add("rational_arithmetic", "basic", f"Вычисли {a}/{b} + {c}/{n}. Ответ — несократимая дробь.", Fraction(a, b)+Fraction(c, n), "Exact Fraction arithmetic")
    x = rng.randint(-20, 20)
    add("linear_equation", "basic", f"Реши уравнение {a}x + {b} = {a*x+b}.", x, "Substitution into linear equation")
    roots = rng.sample(range(-15, 16), 2)
    add("quadratic_vieta", "basic", f"Корни уравнения x² + ({-sum(roots)})x + ({math.prod(roots)}) = 0. Найди сумму квадратов корней.", sum(x*x for x in roots), "Explicit integral roots and Vieta")
    price = 100*(variant+2)
    pct = rng.randint(5, 40)
    add("percent_change", "basic", f"Цена {price}. Её повысили на {pct}%, затем снизили на {pct}%. Найди конечную цену.", Fraction(price*(100+pct)*(100-pct), 10000), "Compose exact multiplicative factors")
    add("arithmetic_sequence", "basic", f"Арифметическая прогрессия: первый член {a}, разность {b}. Найди сумму первых {n} членов.", n*(2*a+(n-1)*b)//2, "Sum explicitly generated progression")
    ratio = variant % 3 + 2
    add("geometric_sequence", "intermediate", f"Геометрическая прогрессия: первый член {a}, знаменатель {ratio}. Найди сумму первых {n} членов.", a*(ratio**n-1)//(ratio-1), "Finite geometric series")
    add("gcd", "basic", f"Найди НОД чисел {a*n} и {b*n}.", math.gcd(a*n, b*n), "Euclid / divisor enumeration")
    add("lcm", "basic", f"Найди НОК чисел {a*n} и {b*n}.", math.lcm(a*n, b*n), "LCM*gcd equals product")
    prime = rng.choice([11, 13, 17, 19])
    exp = rng.randint(30, 100)
    add("modular_power", "intermediate", f"Найди остаток {a}^{exp} по модулю {prime}.", pow(a, exp, prime), "Repeated multiplication cross-check")
    mods = rng.sample([5, 7, 11, 13], 2)
    rem = [rng.randrange(m) for m in mods]
    crt = next(x for x in range(math.prod(mods)) if all(x%m == r for m,r in zip(mods,rem)))
    add("chinese_remainder", "advanced", f"Найди наименьшее неотрицательное x: x mod {mods[0]}={rem[0]}, x mod {mods[1]}={rem[1]}.", crt, "Enumerate complete residue period")
    choose = rng.randrange(1, n)
    add("binomial", "intermediate", f"Сколькими способами выбрать {choose} различных объектов из {n}, если порядок не важен?", math.comb(n, choose), "Count subsets")
    dp = [1, 2]
    for i in range(2, n+1):
        dp.append(dp[-1]+dp[-2])
    add("binary_no_adjacent", "intermediate", f"Сколько двоичных строк длины {n} не содержат двух соседних единиц?", dp[n], "DP and exhaustive binary strings")
    der = [1,0]
    for i in range(2,n+1):
        der.append((i-1)*(der[-1]+der[-2]))
    add("derangements", "advanced", f"Сколько перестановок {n} различных элементов не оставляют ни одного на исходной позиции?", der[n], "Recurrence and inclusion-exclusion")
    target = rng.randint(3, 2*n-1)
    favorable = sum(x+y==target for x in range(1,n+1) for y in range(1,n+1))
    add("dice_probability", "basic", f"Бросили два независимых честных кубика с гранями 1…{n} каждый. Найди вероятность суммы {target}.", Fraction(favorable,n*n), "Enumerate all equiprobable pairs")
    red, blue = variant+3, variant+4
    add("hypergeometric", "intermediate", f"В урне {red} красных и {blue} синих шаров. Без возвращения достали 3. Вероятность ровно 2 красных?", Fraction(math.comb(red,2)*blue,math.comb(red+blue,3)), "Combination count / ordered draws")
    add("conditional_probability", "advanced", f"Бросили честный кубик с гранями 1…{2*n}. Известно, что результат чётный. Найди вероятность, что он кратен 4.", Fraction(n//2,n), "Count conditional sample space")
    add("expectation", "intermediate", f"Равновероятно выбрали целое от 1 до {n}. Найди математическое ожидание квадрата выбранного числа.", Fraction(n*(n+1)*(2*n+1),6*n), "Average explicit squares")
    add("bayes", "advanced", f"Доля дефектных 1/{n}. Чувствительность теста 3/4, вероятность ложного плюса у исправного 1/5. Найди вероятность дефекта при положительном тесте.", Fraction(15,4*n+11), "Bayes with exact joint probability")
    scale = variant+1
    add("triangle_inradius", "intermediate", f"Прямоугольный треугольник имеет катеты {3*scale} и {4*scale}. Найди радиус вписанной окружности.", scale, "Area / semiperimeter")
    add("rectangle_diagonal", "basic", f"Прямоугольник имеет стороны {5*scale} и {12*scale}. Найди длину диагонали.", 13*scale, "Pythagorean triple")
    coords = [(0,0),(a,0),(0,b)]
    add("coordinate_area", "intermediate", f"Найди площадь треугольника с вершинами {coords}.", Fraction(a*b,2), "Cross-product determinant / base-height")
    xx = variant-4
    add("derivative", "intermediate", f"f(x)={a}x³+{b}x²+{c}x+7. Найди f'({xx}).", 3*a*xx*xx+2*b*xx+c, "Power rule")
    bound = variant+1
    add("definite_integral", "intermediate", f"Вычисли интеграл от 0 до {bound}: {a}x²+{b}x+{c}.", Fraction(a*bound**3,3)+Fraction(b*bound**2,2)+c*bound, "Polynomial antiderivative")
    add("polynomial_limit", "intermediate", f"Найди предел (x^{n}-1)/(x-1) при x→1.", n, "Geometric factorization / derivative")
    d = rng.randint(-10,10)
    add("determinant_2x2", "intermediate", f"Вычисли определитель [[{a},{b}],[{c},{d}]].", a*d-b*c, "Signed product difference")
    matrix = [[a,1,0],[0,b,1],[1,0,c]]
    add("determinant_3x3", "intermediate", f"Вычисли определитель {matrix}.", a*b*c+1, "Leibniz permutation formula")
    add("eigenvalue_trace", "intermediate", f"Найди сумму собственных значений матрицы [[{a},{b}],[{c},{d}]] с учётом кратностей.", a+d, "Trace equals eigenvalue sum")
    x0,y0 = rng.randint(-5,5),rng.randint(-5,5)
    add("linear_system", "intermediate", f"Реши систему x+y={x0+y0}, 2x-y={2*x0-y0}. Найди x*y.", x0*y0, "Substitution into invertible system")
    coef = rng.sample(range(-8,9),3)
    aa,bb,cc = coef
    add("newton_sums", "advanced", f"Корни многочлена x³+({aa})x²+({bb})x+({cc}) учитываются с кратностью. Найди сумму кубов всех комплексных корней.", -aa**3+3*aa*bb-3*cc, "Newton identities")
    catalan = math.comb(2*n,n)//(n+1)
    add("catalan", "advanced", f"Сколько правильных скобочных последовательностей с {n} парами круглых скобок?", catalan, "Catalan formula and balanced-prefix DP")
    assert len(result)==30
    return result
