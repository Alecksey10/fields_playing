import random
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import (
    Cookie,
    FastAPI,
    WebSocket,
    WebSocketException,
    status,
)
import sys

sys.path.append('.')


from src.commandor.knowledge.knowledge import Knowledge
from src.commandor.commands_generator import CommandsGenerator
from src.commandor.users_commandor_manager import UsersCommandorsManager
from src.commandor.router import router as router
@asynccontextmanager
async def lifespan(app: FastAPI):
    #инициализируем синглтон
    UsersCommandorsManager()
    yield
    # Clean up the ML models and release the resources
    


app = FastAPI()
app.include_router(router)

