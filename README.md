# Тестовое задание Backend
[![CircleCI](https://circleci.com/gh/Ragnaruk/ws_assets/tree/main.svg?style=shield)](https://circleci.com/gh/Ragnaruk/ws_assets/tree/main)
[![codecov](https://codecov.io/gh/Ragnaruk/ws_assets/branch/main/graph/badge.svg?token=AKR3JFC0WE)](https://codecov.io/gh/Ragnaruk/ws_assets)
[![code-style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![license](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://github.com/Ragnaruk/ws_assets/blob/main/LICENSE)

Сервис для получения данных о котировках валют через websocket.

## Запуск

Для запуска сервиса необходимо уставить все зависимости из `requirements.txt`,
добавить корневую директорию в `PYTHONPATH` и выполнить команду:

```shell
python ws_assets
```

Либо запустить контейнеры `ws_assets` и `postgresql` в `docker-compose.yml` командой:

```shell
docker-compose up -d ws_assets postgresql
```

## База данных

Миграция для базы данных выполнится автоматически при запуске сервиса.

Автоматический запуск включается/выключается переменной окружения: `WS_ASSETS_AUTO_APPLY_MIGRATIONS`.

Вручную миграции применяются командой:

```shell
alembic upgrade head
```

Настройка адреса подключения в файле `alembic.ini`

## UI

У сервиса присутствует страница для тестирования эндпоинта: `http://localhost:8080/`

Отображение страницы включается/выключается переменной окружения: `WS_ASSETS_ENABLE_UI`.

## Websocket

Вебсокет находится по адресу `/api/v1/websocket`

## Формат запросов

### Получение списка активов

Запрос:

```json
{
  "action": "assets",
  "message": {}
}
```

Ответ:

```json
{
  "action": "assets",
  "message": {
    "assets": [
      {
        "id": 1,
        "name": "EURUSD"
      },
      {
        "id": 2,
        "name": "USDJPY"
      },
      {
        "id": 3,
        "name": "GBPUSD"
      },
      {
        "id": 4,
        "name": "AUDUSD"
      },
      {
        "id": 5,
        "name": "USDCAD"
      }
    ]
  }
}
```

### Подписка на котировки актива

Запрос:

```json
{
  "action": "subscribe",
  "message": {
    "assetId": 1
  }
}
```

История за последние 30 минут (ответ сокращен для краткости):

```json
{
  "action": "asset_history",
  "message": {
    "points": [
      {
        "assetName": "EURUSD",
        "time": 1455883484,
        "assetId": 1,
        "value": 1.110481
      },
      {
        "assetName": "EURUSD",
        "time": 1455883485,
        "assetId": 1,
        "value": 1.110948
      },
      {
        "assetName": "EURUSD",
        "time": 1455883486,
        "assetId": 1,
        "value": 1.111122
      }
    ]
  }
}
```

Данные о новой точке:

```json
{
  "action": "point",
  "message": {
    "assetName": "EURUSD",
    "time": 1453556718,
    "assetId": 1,
    "value": 1.079755
  }
}
```

### Сообщения об ошибках

Запрос:

```json
{
  "action": "some_action",
  "message": {}
}
```

Ответ:

```json
{
  "action": "error",
  "message": {
    "error_type": "ValidationError",
    "error_text": "1 validation error for GenericRequest\naction\n unexpected value; permitted: 'assets', 'subscribe' (type=value_error.const; given=some_action; permitted=('assets', 'subscribe'))"
  }
}
```

## Переменные окружения

Список переменных окружения, их описание и дефолтные значения.

```yaml
WS_ASSETS_HOST: Service host. ("0.0.0.0")
WS_ASSETS_PORT: Service port. ("8080")
WS_ASSETS_ENABLE_UI: Enable UI on / path. ("TRUE")
WS_ASSETS_AUTO_APPLY_MIGRATIONS: Automatically apply database migrations on service start. ("TRUE")
WS_ASSETS_LOG_LEVEL: Logging level. ("INFO")
WS_ASSETS_POSTGRESQL_DSN: PostgreSQL DSN. ("postgresql+asyncpg://user:password@localhost:5432/database")
WS_ASSETS_POSTGRESQL_POOL_SIZE: PostgreSQL maximum pool size. ("10")
```

## Тесты

Тесты находятся в папке `tests`. Для их запуска необходимо уставить все зависимости из `requirements.txt`,
потом выполнить команды:

```shell
coverage run --source=./ws_assets -m pytest ./tests -v --disable-pytest-warnings
coverage report
```

Либо запустить контейнер `ws_assets_test` в `docker-compose.yml` командой:

```shell
docker-compose up ws_assets_test
```

### Покрытие тестов

```shell
Name                                            Stmts   Miss  Cover
-------------------------------------------------------------------
ws_assets/__init__.py                               0      0   100%
ws_assets/__main__.py                               5      5     0%
ws_assets/database/__init__.py                      0      0   100%
ws_assets/database/tables.py                        6      0   100%
ws_assets/exceptions.py                            12      2    83%
ws_assets/main.py                                  51     23    55%
ws_assets/models/__init__.py                        0      0   100%
ws_assets/models/asset.py                          16      0   100%
ws_assets/models/base.py                            4      0   100%
ws_assets/models/client.py                         15      1    93%
ws_assets/models/request.py                        21      2    90%
ws_assets/models/response.py                       23      0   100%
ws_assets/routers.py                               11      0   100%
ws_assets/routes/__init__.py                        0      0   100%
ws_assets/routes/api/__init__.py                    0      0   100%
ws_assets/routes/api/v1/__init__.py                 0      0   100%
ws_assets/routes/api/v1/websocket.py               36      0   100%
ws_assets/routes/ui.py                              6      1    83%
ws_assets/settings.py                              20      6    70%
ws_assets/tools/__init__.py                         0      0   100%
ws_assets/tools/asset_processor.py                 68     14    79%
ws_assets/tools/db_client.py                       64     33    48%
ws_assets/tools/meta/__init__.py                    0      0   100%
ws_assets/tools/meta/base_client.py                16      6    62%
ws_assets/tools/mocks/__init__.py                   0      0   100%
ws_assets/tools/mocks/mock_asset_processor.py      23      0   100%
ws_assets/tools/mocks/mock_db_client.py             7      0   100%
ws_assets/tools/websocket_manager.py               42      2    95%
-------------------------------------------------------------------
TOTAL                                             446     95    79%
```

[![codecov-graph](https://codecov.io/gh/Ragnaruk/ws_assets/branch/main/graphs/icicle.svg)](https://codecov.io/gh/Ragnaruk/ws_assets/branch/main/graphs/icicle.svg)

## Дальнейшие шаги

* Добавить семантическое версионирование в CI/CD.
* Добавить автоматическое обновление списка переменных в CI/CD, либо pre-commit хуки.
* Добавить middleware для логирования в Sentry/Jaeger/Prometheus.
* Возможно добавить кэш для записей за последние 30 минут.

## Недостатки

* Основной цикл получения данных из API ждет немного больше 1 секунды из-за издержек запуска таска.
Можно замерять время создания такска и спать `1 - task_creation` секунды,
потом подумать о приоритетном запуске новой итерации цикла, если старое задание
еще не выполнилось и блокирует интепретатор.
* При долгом выполнении запроса на получение истории возможны потери точек,
записанных в базу после получения истории, но до начала подписки. Решается либо общим кэшем точек в памяти,
либо отдельным кэшем для каждого клиента в моделях `WebsocketClient`.
* Если запись точек в базу данных после их получения проваливается, то клиентам они тоже не отправляются.
Решается распараллеливанием задач записи в базу и отправки клиентам.
Зависит от важности поддержки консистентности между базой данных и локальными данными клиента.