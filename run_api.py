"""
Скрипт для запуска FastAPI сервера Budget Tracker
"""
import uvicorn
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

if __name__ == "__main__":
    print("🚀 Запуск Budget Tracker API сервера...")
    print("📖 Документация доступна по адресу: http://localhost:8000/docs")
    print("🌐 API доступно по адресу: http://localhost:8000")
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоматическая перезагрузка при изменениях
        log_level="info"
    )
