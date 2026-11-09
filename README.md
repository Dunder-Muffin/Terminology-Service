# Terminology service

Сервис терминологии - хранилище справочников с версиями и REST API к нему.

Стек: Python 3.12+, Django 6.1, Django REST Framework, drf-spectacular, SQLite.

## Запуск

```bash
python3 -m venv venv
source venv/bin/activate
make install
cp .env.example .env
make migrate
python manage.py createsuperuser
make run
```

- Админка: http://127.0.0.1:8000/admin/
- Swagger: http://127.0.0.1:8000/api/docs/

## API

| Метод | Описание |
|---|---|
| `GET /refbooks/?date=YYYY-MM-DD` | список справочников, `date` опционально |
| `GET /refbooks/<id>/elements/?version=<version>` | элементы версии справочника, без `version` - текущей версии |
| `GET /refbooks/<id>/check_element/?code=<code>&value=<value>&version=<version>` | проверка что элемент есть в версии справочника |

Подробнее с примерами в swagger.

## Тесты и линтер

```bash
make test
make lint
```

Ruff также запускается через pre-commit при каждом коммите.
