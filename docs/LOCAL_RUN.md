# Запуск своей модели на ПК

## Что уже должно быть

Git, Python 3.11+, модель, загруженная в локальный сервер. Сам файл `.gguf` без работающего сервера недостаточен. На время прогона сервер должен оставаться включённым. AxiomBench не дообучает и не изменяет веса модели.

Для General/Math Docker не требуется. Для C++ установи Docker Desktop, включи Linux-контейнеры, дождись готовности Docker engine и один раз выполни `docker pull gcc:14`.

Официальные инструкции серверов, проверенные 2026-10-07:

- LM Studio: https://lmstudio.ai/docs/developer/core/server
- LM Studio OpenAI compatibility: https://lmstudio.ai/docs/developer/openai-compat
- Ollama: https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx
- llama.cpp: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

## LM Studio / Windows

Загрузи выбранную модель, запусти сервер в Developer. Используй показанный приложением адрес. По умолчанию это порт 1234.

```powershell
git clone https://github.com/DSIFYB/AxiomBench.git
cd AxiomBench
py scripts/run_local.py --track math --profile quick
```

Python launcher `py` может отсутствовать. В таком случае попробуй `python` вместо `py`, если эта команда указывает на Python 3.11+. Launcher берёт исходники прямо из репозитория и не требует `pip install` для обычного запуска.

Если API показывает несколько моделей, укажи точный ID. Посмотреть ID без установки пакета:

```powershell
$env:PYTHONPATH = "src"
py -m axiombench.cli models --base-url http://127.0.0.1:1234/v1
py scripts/run_local.py --model "ID_МОДЕЛИ" --track math --profile quick
```

Для всех направлений:

```powershell
docker pull gcc:14
py scripts/run_local.py --model "ID_МОДЕЛИ" --profile quick
```

Полный набор:

```powershell
py scripts/run_local.py --model "ID_МОДЕЛИ" --profile full
```

## Пауза и продолжение

Выбери постоянный файл результатов перед длинным прогоном:

```powershell
py scripts/run_local.py --model "ID_МОДЕЛИ" --profile full --answers results/full-attempt.jsonl
```

Остановить можно Ctrl+C. После включения того же сервера продолжить:

```powershell
py scripts/run_local.py --model "ID_МОДЕЛИ" --profile full --answers results/full-attempt.jsonl --resume
```

Сохранённые строки пропускаются; конфигурация должна совпадать. Уже записанные ошибки API не пересылаются автоматически. Если последняя строка повреждена из-за прерывания записи, CLI остановится и потребует исправления файла; он не удаляет её незаметно. Запрос, ответ на который не успел сохраниться, при продолжении может отправиться ещё раз, поэтому такой прогон нельзя считать строго гарантированным one-request-per-item. Для чистого сравнительного запуска используй новый файл и непрерывный прогон.

## Отдельные направления / лимит ответа

```powershell
py scripts/run_local.py --model "ID_МОДЕЛИ" --track general --profile full
py scripts/run_local.py --model "ID_МОДЕЛИ" --track cpp --profile quick
py scripts/run_local.py --model "ID_МОДЕЛИ" --track math --profile full --max-tokens 8192
```

По умолчанию launcher даёт 4096 выходных токенов и делает один запрос за раз. Увеличение `max-tokens` не меняет автоматически длину контекста или внутренний reasoning budget сервера. У разных моделей эти параметры нужно фиксировать отдельно.

## Где результат

`results/<timestamp>-<profile>-<track>.jsonl` — ответы. Соседний `.meta.json` — параметры и hashes. `.report.json` — подробные результаты. `.report.html` — файл для просмотра в браузере: четыре оценки и таблица задач. Пустые направления обозначены прочерком. Для General/Math оценивается итоговый ответ, для C++ нужно пройти все проверочные случаи.

## Частые проблемы

| Сообщение | Действие |
|---|---|
| Connection refused / preflight failed | Включить сервер, проверить base URL и порт |
| Specify --model | Указать точный ID модели из `/v1/models` |
| Docker required / image unavailable | Запустить Docker Desktop, скачать gcc:14; либо выбрать General/Math |
| Resume configuration mismatch | Вернуть исходные model/profile/track/max-tokens/base URL; для новых условий использовать новый файл |
| invalid_format | Посмотреть ответ: ожидался один JSON с answer либо один полный cpp-блок |
| API ERROR | Проверить сервер; запуск останавливает новые запросы, оставляет собранные ответы |
| finish_reason=length | Ответ обрезан; следующий отдельный прогон провести с большим лимитом и зафиксировать его |

Если модель выдаёт `<think>` в обычном content, это может нарушить требуемый формат JSON. Настрой разделение reasoning/content на сервере или оценивай формат как отдельное ограничение; evaluator не вырезает рассуждения произвольными эвристиками.

Обновить репозиторий: `git pull`. Если benchmark/evaluator изменились, старые метаданные и новый набор не совпадут. Для сравнения сохрани прежний commit или начинай новый прогон, не смешивай версии.
