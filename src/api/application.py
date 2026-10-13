from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
import inspect
import os

from src.api import routers
from src.app.base import Application

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
    return config.get("routers", {}).get(name, True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    Application lifespan

    Args:
        app: FastAPI application
    '''
    global INSTANCE

    # Instantiate Application using the CONFIG environment variable path
    config_path = os.environ.get("CONFIG", "config.yml")
    INSTANCE = Application(config_path)

    config = INSTANCE.config

    routers = api_routers()
    for name, router in routers.items():
        if enabled(config, name):
            app.include_router(router)

    print("application is starting")
    
    yield
    
    if INSTANCE:
        await INSTANCE.close()
    print("application is stopped")


def create():
    '''
    Create a new application instance

    Returns:
        FastAPI: application instance
    '''
    app = FastAPI(lifespan=lifespan)
    return app

app = create()