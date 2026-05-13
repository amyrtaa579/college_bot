"""
College Bot API — REST API для чат-бота.
Предоставляет данные для Max-бота (или любого другого клиента).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.controllers import about, specialties, admission, faq

app = FastAPI(
    title="College Bot API",
    description="API для чат-бота абитуриентов колледжа",
    version="0.1.0"
)

# CORS для запросов с любого источника (в продакшене — ограничить)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(about.router, prefix="/api")
app.include_router(specialties.router, prefix="/api")
app.include_router(admission.router, prefix="/api")
app.include_router(faq.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "College Bot API", "version": "0.1.0"}