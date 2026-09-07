import uvicorn
from src.config import settings, get_app

app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port if hasattr(settings, "port") else 8001,
        reload=settings.debug
    )