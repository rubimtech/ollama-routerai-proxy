# Enchanted Proxy для RouterAI

[![GitHub](https://img.shields.io/badge/GitHub-ollama--routerai--proxy-blue?style=flat-square&logo=github)](https://github.com/rubimtech/ollama-routerai-proxy)
[![Go Version](https://img.shields.io/badge/Go-1.22+-00ADD8?style=flat-square&logo=go)](https://go.dev/)

Прокси-сервер, эмулирующий [REST API Ollama](https://github.com/ollama/ollama), но перенаправляющий запросы в [RouterAI](https://routerai.ru) — российский OpenAI-совместимый API-шлюз с оплатой в рублях.

Создан для использования с [Enchanted](https://github.com/rubimtech/enchanted/tree/main), но подходит для любых инструментов, требующих Ollama-совместимой конечной точки.

Оригинальный автор прокси — [marknefedov](https://github.com/marknefedov/ollama-openrouter-proxy).

---

## Содержание
- [Описание](#описание)
- [Возможности](#возможности)
- [Установка](#установка)
- [Настройка](#настройка)
- [API эндпоинты](#api-эндпоинты)
- [Интеграция](#интеграция-с-инструментами)
- [Примеры](#примеры)
- [Устранение неполадок](#устранение-неполадок)

---

## Описание

Этот репозиторий предоставляет прокси-сервер, который эмулирует [REST API Ollama](https://github.com/ollama/ollama), но перенаправляет запросы в [RouterAI](https://routerai.ru) (или любую другую OpenAI-совместимую конечную точку). Под капотом используется библиотека [sashabaranov/go-openai](https://github.com/sashabaranov/go-openai) с минимальными изменениями кода для сохранения совместимости с API Ollama.

Это позволяет использовать инструменты и клиенты, совместимые с Ollama, выполняя запросы к моделям, управляемым через RouterAI.

Помимо стандартного Ollama-формата, прокси предоставляет нативную OpenAI-совместимую конечную точку /v1/chat/completions, что позволяет использовать его напрямую с любыми OpenAI-клиентами.

---
## Возможности

| Возможность | Описание |
|---|---|
| **Ollama-совместимый API** | Полная эмуляция REST API Ollama на порту 11436 |
| **OpenAI-совместимый API** | Нативный эндпоинт /v1/chat/completions |
| **Стриминг** | Потоковые ответы в NDJSON (Ollama) и SSE (OpenAI) |
| **Фильтрация моделей** | Ограничение списка моделей через файл models-filter |
| **Любой провайдер** | Работа с любым OpenAI-совместимым API |
| **Поддержка Tools** | Передача вызовов инструментов |
| **Два режима чата** | Обычный и потоковый режимы |

---

## Установка

### 1. Сборка из исходников

Требования: Go 1.22 или новее.

```
git clone https://github.com/rubimtech/ollama-routerai-proxy
cd ollama-routerai-proxy
go mod tidy
go build -o ollama-proxy
```

### 2. Docker

```
docker build -t ollama-routerai-proxy .
docker run -d --name ollama-proxy -e OPENAI_API_KEY="sk-i-..." -e OPENAI_BASE_URL="https://routerai.ru/api/v1" -p 11436:11436 ollama-routerai-proxy
```

### 3. Docker Compose

```
docker compose up -d
```

---

## Настройка

### Переменные окружения

- OPENAI_API_KEY (обязательно) - API-ключ RouterAI или другого провайдера
- OPENAI_BASE_URL (опционально) - базовый URL API, по умолчанию https://routerai.ru/api/v1

### Аргументы командной строки

```
./ollama-proxy "sk-i-ваш-ключ"
./ollama-proxy "https://routerai.ru/api/v1" "sk-i-ваш-ключ"
```

Приоритет: переменные окружения имеют приоритет над аргументами командной строки.

### Фильтрация моделей

Создайте файл models-filter в директории с прокси. Каждая строка - полное имя модели:

```
deepseek/deepseek-chat-v3.1
openai/gpt-4o
```

Если файла нет или он пуст - фильтрация не применяется.

---

## API эндпоинты

### GET / - проверка состояния

```
curl http://localhost:11436/
```

Ожидаемый ответ: Ollama is running

### GET /api/tags - список моделей

```
curl http://localhost:11436/api/tags
```

### POST /api/show - детали модели

```
curl -X POST http://localhost:11436/api/show -H "Content-Type: application/json" -d '{"name":"deepseek-chat-v3.1"}'
```

### POST /api/chat - чат (Ollama-формат)

```
curl -N -X POST http://localhost:11436/api/chat -H "Content-Type: application/json" -d '{"model":"deepseek-chat-v3.1","messages":[{"role":"user","content":"Привет!"}]}'
```

### POST /v1/chat/completions - чат (OpenAI-формат)

```
curl -X POST http://localhost:11436/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"deepseek-chat-v3.1","messages":[{"role":"user","content":"Привет!"}]}'
```

---

## Интеграция с инструментами

### Open WebUI

Подключите Open WebUI к прокси, указав в настройках:

- URL: http://localhost:11436
- API-ключ: не требуется

Или при запуске контейнера:

```
docker run -d --name open-webui -e OLLAMA_BASE_URL=http://host.docker.internal:11436 -p 3000:8080 ghcr.io/open-webui/open-webui:main
```

### Enchanted

В приложении Enchanted (iOS/macOS):

1. Откройте настройки.
2. Укажите URL сервера: http://IP-адрес-компьютера:11436
3. Прокси автоматически подключится к RouterAI.

---

## Примеры

### Python (обычный режим)

```
import requests

url = "http://localhost:11436/api/chat"
payload = {"model": "deepseek-chat-v3.1", "messages": [{"role": "user", "content": "Привет!"}], "stream": False}
response = requests.post(url, json=payload)
print(response.json()["message"]["content"])
```

### Python (потоковый режим)

```
import requests
import json

url = "http://localhost:11436/api/chat"
payload = {"model": "deepseek-chat-v3.1", "messages": [{"role": "user", "content": "Расскажи анекдот."}], "stream": True}
with requests.post(url, json=payload, stream=True) as r:
    for line in r.iter_lines():
        if line:
            data = json.loads(line)
            content = data["message"].get("content", "")
            if content:
                print(content, end="", flush=True)
            if data.get("done"):
                print()
                break
```

---

## Устранение неполадок

### Прокси не запускается
- Убедитесь, что OPENAI_API_KEY установлен.
- Проверьте, что порт 11436 не занят: netstat -ano | findstr :11436

### Ошибка 404 model not found
- Укажите полное имя модели (с префиксом вендора, например deepseek/deepseek-chat-v3.1).
- Проверьте доступность модели через RouterAI.

### Пустой список моделей
- Проверьте models-filter на неверные имена моделей.
- Удалите файл фильтра для отображения всех моделей.

---

## Лицензия

Распространяется под лицензией MIT.

Связанные проекты:
- Enchanted - iOS/macOS клиент для Ollama
- RouterAI - OpenAI-совместимый API-шлюз с оплатой в рублях
- Оригинальный прокси от marknefedov
