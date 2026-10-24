# src/api/application.py
import importlib
import pkgutil
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api_manager.api import routers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway starting up...")
    yield
    logger.info("API Gateway shutting down...")

def create_application() -> FastAPI:
    app = FastAPI(title="CMS-0057-F Enterprise API Gateway", lifespan=lifespan)
    
    # Automatically discover and register ALL routers in api_manager/api/routers/
    # As you add crd.py, dtr.py, pas.py, they are automatically mounted!
    for _, module_name, _ in pkgutil.iter_modules(routers.__path__):
        module = importlib.import_module(f"api_manager.api.routers.{module_name}")
        if hasattr(module, "router"):
            app.include_router(module.router)
            logger.info("Auto-registered router module: %s", module_name)
            
    return app

app = create_application()