import uvicorn

from src.infra.celery.setup import app as celery_app
from src.presentation.api.builder import AppBuilder

app = AppBuilder.create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
