import importlib
import pkgutil
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from payer_A.api import routers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Payer A Core Engine starting up...")
    yield
    logger.info("Payer A Core Engine shutting down...")

def create_payer_app() -> FastAPI:
    app = FastAPI(title="Payer A Core System", lifespan=lifespan)
    
    # Automatically scan and register ALL routers in payer_A/routers/
    # Exactly mirrors the API Manager design—zero manual wiring required.
    for _, module_name, _ in pkgutil.iter_modules(routers.__path__):
        module = importlib.import_module(f"payer_A.api.routers.{module_name}")
        if hasattr(module, "router"):
            app.include_router(module.router)
            logger.info("Auto-registered payer router module: %s", module_name)
            
    return app

app = create_payer_app()