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

Разрешените CORS адреси се задават с `TECHRESCUE_CORS_ORIGINS` — списък, разделен със запетаи
(или JSON масив), например `TECHRESCUE_CORS_ORIGINS=http://localhost:3000,http://192.168.0.38:3000`.
Без съответния адрес в този списък браузърът блокира заявките от frontend-а.

API документацията е достъпна на `http://localhost:8000/docs`.

## Начален API обхват

- `authentication` — регистрация, вход и изход (`POST /api/v1/auth/logout`) с bearer session token
- `users` — текущ профил
- `chat` — защитени чат съобщения, списък на разговорите и история на съобщенията
- `AI` — базова диагностика
- `knowledge base` — публично четене и admin създаване на статии
- `tickets` — създаване и списък на тикети
- `subscriptions` — текущ план
- `admin` — административна статистика

Потребителските профили, хешовете на сесиите, разговорите и съобщенията се съхраняват в PostgreSQL.
Таблиците `conversations` и `messages` са свързани с външни ключове; разговорите са достъпни само от собственика им.
Базовият план за абонамент се пази в `users.subscription`. Билетите (`tickets`) и статиите в базата знания
(`knowledge_articles`) също се съхраняват в PostgreSQL.

Опитите за вход и регистрация са ограничени по IP и имейл (`TECHRESCUE_LOGIN_ATTEMPT_LIMIT`,
по подразбиране 10 за `TECHRESCUE_LOGIN_ATTEMPT_WINDOW_SECONDS` = 300 секунди). Броячът се пази в
паметта на процеса, така че при повече от един worker е нужно общо хранилище (Redis).

Сесиите имат срок на валидност (`auth_sessions.expires_at`), който се конфигурира с
`TECHRESCUE_SESSION_TTL_HOURS` (по подразбиране 168 часа). Изтеклите сесии се изчистват при вход и регистрация и
връщат 401 при използване; logout изтрива сесията незабавно.

## Тестове

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

Тестовете използват in-memory SQLite и не изискват PostgreSQL.
