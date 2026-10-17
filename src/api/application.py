from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
import inspect
import logging
import os

from src.api import routers
from src.app.base import Application

logger = logging.getLogger(__name__)
# logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

INSTANCE = None

def get():
    '''
    Get the application instance.
    '''
    return INSTANCE

def api_routers() -> dict:
    '''
    Get available API routers

    Returns:
        {router name: router instance}
    '''
    available = {}
    for name, module in inspect.getmembers(routers, inspect.ismodule):
        if hasattr(module, "router") and isinstance(module.router, APIRouter):
            available[name] = module.router
    logger.info("Discovered routers: %s", list(available))
    return available

def enabled(config, name):
    '''
    Check if a router is enabled

    Args:
        config (dict): application configuration
        name (str): router name

    Returns:
        bool: True if enabled, False otherwise
    '''
    is_enabled = config.get("routers", {}).get(name, True)
    logger.info("Router %s enabled=%s", name, is_enabled)
    return is_enabled


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Application lifespan

    Args:
        app: FastAPI application
    '''
    global INSTANCE
    logging.getLogger().setLevel(logging.INFO)

    config_path = os.environ.get("CONFIG")
    logger.info("Loading config from %s", config_path)
    INSTANCE = Application(config_path)

    config = INSTANCE.config

    routers = api_routers()
    for name, router in routers.items():
        if enabled(config, name):
            app.include_router(router)
            logger.info("Included router %s", name)

    logger.info("Application is starting")
    
    yield
    
    if INSTANCE:
        await INSTANCE.close()
    logger.info("Application is stopped")


def create():
    '''
    Create a new application instance

    Returns:
        FastAPI: application instance
    '''
    app = FastAPI(lifespan=lifespan)
    return app

app = create()