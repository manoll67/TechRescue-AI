# TechRescue FastAPI backend

## Стартиране

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

По подразбиране API използва `postgresql+psycopg://techrescue:techrescue@localhost:5432/techrescue`.
За различна база задайте `TECHRESCUE_DATABASE_URL` (например в `.env`).
Промените в схемата се управляват с Alembic; приложението не създава таблици автоматично.

API документацията е достъпна на `http://localhost:8000/docs`.

## Начален API обхват

- `authentication` — регистрация и вход с bearer session token
- `users` — текущ профил
- `chat` — защитени чат съобщения
- `AI` — базова диагностика
- `knowledge base` — публично четене и admin създаване на статии
- `tickets` — създаване и списък на тикети
- `subscriptions` — текущ план
- `admin` — административна статистика

Потребителските профили, хешовете на сесиите, разговорите и съобщенията се съхраняват в PostgreSQL.
Таблиците `conversations` и `messages` са свързани с външни ключове; разговорите са достъпни само от собственика им.
Базовият план за абонамент се пази в `users.subscription`. Данните за билетите и базата знания остават in-memory.
