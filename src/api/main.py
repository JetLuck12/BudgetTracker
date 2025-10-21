"""
Основной файл FastAPI приложения для Budget Tracker
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

# Импортируем роутеры
from .routers import transactions, plan, analytics, import_router

# Создаем приложение FastAPI
app = FastAPI(
    title="Budget Tracker API",
    description="API для управления личным бюджетом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настраиваем CORS для веб-клиента
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене следует указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(transactions.router)
app.include_router(plan.router)
app.include_router(analytics.router)
app.include_router(import_router.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с информацией об API"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Budget Tracker API</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #27ae60; }
            .url { font-family: monospace; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💸 Budget Tracker API</h1>
            <p>Добро пожаловать в API для управления личным бюджетом!</p>
            
            <h2>📚 Документация</h2>
            <p>
                <a href="/docs" target="_blank">Swagger UI</a> | 
                <a href="/redoc" target="_blank">ReDoc</a>
            </p>
            
            <h2>🔗 Основные endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> 
                <span class="url">/api/transactions</span> - Получить все транзакции
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> 
                <span class="url">/api/transactions</span> - Создать новую транзакцию
            </div>
            
            <div class="endpoint">
                <span class="method">DELETE</span> 
                <span class="url">/api/transactions/{id}</span> - Удалить транзакцию
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> 
                <span class="url">/api/plan</span> - Получить план бюджета
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> 
                <span class="url">/api/plan</span> - Создать план бюджета
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> 
                <span class="url">/api/analytics/summary</span> - Получить финансовую сводку
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> 
                <span class="url">/api/import/csv</span> - Импорт из CSV
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> 
                <span class="url">/api/import/excel</span> - Импорт из Excel
            </div>
            
            <h2>🚀 Быстрый старт</h2>
            <p>Для запуска сервера используйте:</p>
            <pre>uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000</pre>
            
            <h2>📱 Примеры использования</h2>
            <p>API поддерживает JSON формат и может использоваться с любыми клиентами:</p>
            <ul>
                <li>Веб-приложения</li>
                <li>Мобильные приложения</li>
                <li>Скрипты автоматизации</li>
                <li>Интеграции с банками</li>
            </ul>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {"status": "healthy", "message": "Budget Tracker API работает"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
