# Формат задания

Файл UTF-8 JSONL, одна JSON-запись на строку. `axiombench validate` проверяет обязательные поля, уникальность ID и базовую согласованность вида задания.

| Поле | Назначение |
|---|---|
| id | Уникальный и стабильный строковый ID |
| track | general / cpp / math |
| kind | json / cpp / number |
| category | Поднавык: logic, algebra, overflow и т.д. |
| difficulty | basic / intermediate / advanced; в v0.1 предварительная авторская оценка |
| prompt | Условие без ожидаемого ответа |
| source | Происхождение задачи |
| license | Разрешённая лицензия для самой задачи |
| split | dev / eval; опубликованный starter целиком dev |
| created_at | Дата создания задачи; не дата обучения модели |
| answer | Ожидаемый JSON-ответ или точное число; для json/number |
| mode | generation / repair; только cpp |
| buggy_code | Полный исходник с ошибкой; для cpp repair |
| tests | Массив объектов со строковыми stdin/stdout; только cpp |
| reference | Путь доверенного эталона относительно папки набора; необязателен для evaluator |

Пример:

```json
{"id":"my-math-001","track":"math","kind":"number","category":"probability","difficulty":"intermediate","prompt":"Вероятность выпадения 6 на честном шестигранном кубике?","answer":"1/6","source":"Original task","license":"MIT","split":"dev","created_at":"2026-10-07"}
```

Экспорт оставляет только id, track, сформированный prompt. Ответы, tests и reference не экспортируются. Buggy code включается в repair prompt, поскольку это вход задачи.

Ответы модели: `{"id":"...","response":"полный текст ответа"}`. Дополнительно сборщик сохраняет prompt_sha256, latency_seconds, usage и finish_reason. Поле error обозначает сбой получения ответа, а не неверное решение.

Стартовый файл можно пересобрать через `python tools/build_starter.py`. Менять опубликованную версию без смены версии набора нельзя. Для внешних данных потребуется manifest из [SOURCES](SOURCES.md); базовый JSONL формат не является готовым адаптером всех перечисленных бенчмарков.

## Extended v0.2

Файл `tasks.jsonl.gz` содержит тот же UTF-8 JSONL, сжатый gzip. Поля family и variant обозначают базовое семейство и параметрический вариант; mode отделяет C++ generation и repair. Quick выбирает первую задачу каждой family/mode группы; Full сохраняет все. Поле verification_method описывает авторский проверочный метод и не передаётся модели. Manifest закрепляет compressed bytes и эталоны. Статистическая зависимость вариантов сохраняется независимо от наличия 900 уникальных prompt strings.
