from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routers import admin, ai, authentication, chat, knowledge, subscriptions, tickets, users

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


for router in (
    authentication.router,
    users.router,
    chat.router,
    ai.router,
    knowledge.router,
    tickets.router,
    subscriptions.router,
    admin.router,
):
    app.include_router(router, prefix=settings.api_prefix)
