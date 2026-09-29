# TechRescue-AI

Next.js интерфейс и FastAPI backend за AI техническа поддръжка.

## Frontend (Next.js)

```bash
npm install
npm run dev
```

Адресът на API се задава с `NEXT_PUBLIC_API_URL` (по подразбиране `http://localhost:8000/api/v1`),
например в `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Интерфейсът поддържа регистрация, вход, изход и чат през backend-а; токенът се пази в `localStorage`.

## Backend (FastAPI)

Вж. [backend/README.md](backend/README.md).
