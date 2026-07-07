import uvicorn
from src.config import settings
from src.application import get_app

app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "service2.src.main:app",
        host=settings.service2_host,
        port=settings.service2_port,
        reload=True
    )