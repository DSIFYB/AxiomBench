# AxiomBench

**Reason. Code. Solve.**

Сборка бенчмарков для локальных и API-моделей: **общий интеллект / рассуждение**, **написание и исправление C++**, **математика**.

## Основной набор v0.3

| Направление | Quick | Full |
|---|---:|---:|
| Рассуждение | 35 | 350 |
| Написание C++ | 15 | 150 |
| Исправление C++ | 25 | 250 |
| Математика | 35 | 350 |
| **Всего** | **110** | **1100** |

Для 400 заданий C++ включено **10 120 stdin/stdout проверочных случаев**, включая 320 записей больших stress-тестов. В repair: **150 логических исправлений и 100 задач на синтаксис/ошибки компиляции**. Проверяются 250 эталонных исходников, 150 логических мутаций и 100 исходников, которые обязаны не компилироваться. Starter на 32 задачи и Extended v0.2 на 900 задач сохранены без изменения.

**Состав:** 35 семейств рассуждения, 35 математических, 15 алгоритмических C++ × два режима и 10 семейств syntax repair. В каждой группе — 10 параметрических вариантов. Это **1100 заданий из 95 базовых семейств**, а не 1100 независимых вручную составленных задач. Набор публичный, синтетический, предназначен для development и диагностики; сложность ещё не откалибрована на моделях. Баллы не означают IQ и не равны официальным баллам сторонних бенчмарков.

В v0.3 устранены постоянные ответы в десяти прежних семействах General; boolean-семейства сбалансированы 5/5. Добавлены цепочки импликаций, ограничения позиций, выполнение программы регистра, составные операции над множествами, параллельное расписание; в математике — условная вероятность, оптимизация и комбинированный подсчёт. Алгоритмические C++ семьи получили большие входы и CPU-бюджет 1 секунда на случай. Три намеренно неэффективных решения проверяются на отклонение. Это не формальное доказательство асимптотики всех программ.

**Syntax repair** включает пропущенные `;`, скобки и `}`, ошибку шаблона, неизвестный идентификатор, недостающий заголовок/namespace, неверный оператор ввода, некорректный тип и объявление ссылки. Нужно вернуть полный исходник, который компилируется и выдаёт правильные ответы. В HTML/JSON синтаксические и логические исправления показаны отдельно.

## Как это работает на твоём ПК

1. `git clone` скачивает задания и проверяющий код.
2. Ты загружаешь свою модель в LM Studio, Ollama, llama.cpp или другой сервер с API `chat/completions`.
3. AxiomBench последовательно отправляет задания **твоей локальной модели**. Модель не скачивается и не запускается автоматически.
4. Проверяются итоговые ответы; C++ компилируется и запускается в Docker.
5. Получаешь JSON с подробностями и HTML-отчёт с итоговым баллом **0–100** и четырьмя отдельными оценками.

**Итоговый балл** — среднее процентов General, Math, C++ generation и C++ repair: каждое направление весит 25%. Например, `(62 + 48 + 46 + 56) / 4 = 53 / 100`. В HTML крупно показан целый балл, а рядом и в JSON — значение с двумя десятичными знаками. JSON сохраняет формулу под именем `overall.protocol = equal-four-v1`.

Сравнивай модели на одном SHA-256 набора, одном профиле и одинаковых настройках генерации и проверки. Quick и Full ведутся отдельно. Итоговый балл доступен только при наличии всех четырёх направлений; пропуски и ошибки API делают его предварительным. Разница 50 против 53 означает преимущество по среднему на этом наборе, но сама по себе не доказывает устойчивое превосходство модели.

Для обычного запуска нужен **Python 3.11+**. Для C++ дополнительно нужен запущенный Docker с Linux-контейнерами. GPU использует сервер модели; AxiomBench сам модель в VRAM не загружает. После скачивания репозитория и образа компилятора локальный прогон не требует интернета.

## Самый простой запуск — Windows / PowerShell

```powershell
git clone https://github.com/DSIFYB/AxiomBench.git
cd AxiomBench
```

Загрузи модель в **LM Studio**, открой **Developer** и запусти локальный сервер. Адрес по умолчанию — `http://127.0.0.1:1234/v1`. Для первого запуска достаточно математики, Docker не нужен:

```powershell
py scripts/run_local.py --track math --profile quick
```

Если сервер показывает ровно одну модель, её ID выберется автоматически. Если моделей несколько:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m axiombench.cli models --base-url http://127.0.0.1:1234/v1
py scripts/run_local.py --model "ID_МОДЕЛИ" --track math --profile quick
```

Для всех направлений включи Docker Desktop и скачай образ компилятора:

```powershell
docker pull gcc:14
py scripts/run_local.py --model "ID_МОДЕЛИ" --profile quick
py scripts/run_local.py --model "ID_МОДЕЛИ" --profile full
```

`quick` — 110 заданий, `full` — 1100. В конце команда напечатает путь к `.report.html`; открой файл браузером. Время полного прогона зависит от скорости модели, длины ответов и Docker. Результаты сохраняются в `results/` и автоматически на GitHub не отправляются.

На Linux/macOS используй `python3` вместо `py`. Подробнее: [LOCAL_RUN](docs/LOCAL_RUN.md).

## Другие серверы модели

| Сервер | Обычно используемый base URL |
|---|---|
| LM Studio | `http://127.0.0.1:1234/v1` |
| Ollama | `http://127.0.0.1:11434/v1` |
| llama.cpp / llama-server | `http://127.0.0.1:8080/v1` |

```powershell
py scripts/run_local.py --base-url http://127.0.0.1:11434/v1 --model "ИМЯ_В_OLLAMA" --track general --profile quick
```

Проверь фактический порт и модель на своём сервере. Поддерживается базовый OpenAI-совместимый `chat/completions`; дополнительные provider-specific reasoning-параметры не передаются. При необходимости ключ задаётся в `AXIOMBENCH_API_KEY`.

## CLI: собирать и проверять отдельно

```bash
python -m pip install -e .
axiombench --profile full validate
axiombench --track math --profile quick export --output results/prompts.jsonl
axiombench --track math --profile full run --model your-model --output results/math-full.jsonl
axiombench --track math --profile full grade --predictions results/math-full.jsonl --output results/math-full-report.json
```

У `run` и `grade` должны совпадать suite, track и profile. Сборщик сохраняет hashes, модель, настройки, usage и latency. При паузе/прерывании поддерживается `run --resume`: сохранённые ответы не запрашиваются повторно. Подробности и ограничения: [протокол](docs/EVALUATION.md).

Исходный набор:

```bash
axiombench --suite benchmarks/starter-v0.1/tasks.jsonl validate
axiombench --suite benchmarks/extended-v0.2/tasks.jsonl.gz --profile full validate
```

Сравнение сохранённых результатов нескольких моделей:

```powershell
py scripts/compare_models.py results/quazar.report.json results/other.report.json
```

Команда выводит рейтинг и разницу с ориентировочным 95% bootstrap-интервалом, повторно выбирая **семейства**, а не считая зависимые варианты независимыми. Разные наборы, профили, версии проверяющего кода, лимиты генерации, компиляторы или незавершённые прогоны не объединяются. Если интервал включает 0, разница неубедительна при этом методе. Это анализ конкретного публичного набора, а не доказательство общего превосходства модели. Между версиями v0.2/v0.3 баллы ведутся отдельно.

## Современная методологическая основа

| Направление | Источники |
|---|---|
| General | [MMLU-Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro), [GPQA](https://github.com/idavidrein/gpqa), [LiveBench](https://github.com/LiveBench/LiveBench) |
| Обобщение / агенты | [ARC-AGI-2](https://arcprize.org/arc-agi/2), [ARC-AGI-3](https://arcprize.org/arc-agi/3) |
| C++ | [LiveCodeBench Pro](https://github.com/GavinZhengOI/LiveCodeBench-Pro), [LiveCodeBench](https://github.com/LiveCodeBench/LiveCodeBench), [Aider Polyglot](https://aider.chat/docs/leaderboards/) |
| Математика | [MathArena](https://github.com/eth-sri/matharena), [AIME 2026 / HMMT 2026](https://matharena.ai/competitions) |
| Экспертный будущий слой | [HLE](https://lastexam.ai/), [FrontierMath](https://epoch.ai/frontiermath) |

Эти источники используются как ориентиры дизайна и дальнейшей интеграции. **Их задания не включены в текущие 1100**, адаптеры официальных наборов пока не реализованы. Текущий General охватывает рассуждение и инструкции, но не полную предметную широту MMLU-Pro. ARC-AGI-3 требует отдельного интерактивного harness. Подробности: [SOURCES](docs/SOURCES.md).

## Проверить сборку

```bash
python -m unittest discover -s tests -v
python tools/verify_references.py
python tools/verify_math.py
python tools/verify_extended.py --jobs 2
python tools/verify_quality_text.py
python tools/verify_quality_cpp.py --jobs 2
```

Для проверок эталонных C++ программ нужен локальный GCC, а не Docker. Это отдельные developer-команды для **доверенных файлов репозитория**; ответы моделей проверяются только через контейнерный `grade`. Проверка v0.3 компилирует 250 эталонов и 250 ошибочных вариантов и может занять несколько минут. Команды проверки CPU-лимитов используют Linux; Docker grading подходит для Windows с Linux engine.

Генераторы `tools/build_starter.py` и `tools/build_extended.py` воспроизводят публичные наборы из фиксированных seeds. Quality v0.3 пересобирается через `python tools/build_quality.py`. Набор хранится в `tasks.jsonl.gz`, большие случаи — в gzip-файлах fixtures с закреплёнными SHA-256; CLI проверяет их при загрузке. [Формат данных](docs/DATASET_FORMAT.md), [методология](docs/EVALUATION.md), [план развития](docs/ROADMAP.md), [внесение задач](CONTRIBUTING.md).

Код и наши исходные задания — MIT. Реальные результаты моделей пока не опубликованы.
