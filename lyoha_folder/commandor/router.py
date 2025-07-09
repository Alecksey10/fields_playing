from fastapi import APIRouter, Response
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

from fastapi.responses import JSONResponse

from commands.init_driver import InitDriver
from commands.run_driver import RunDriver
from commands.shutdown_driver import ShutdownDriver


sys.path.append('.')
from commands.bilet_commands.choose_bilet import ChooseBilet
from commandor.knowledge.knowledge import Knowledge
from commandor.commands_generator import CommandsGenerator
from commandor.users_commandor_manager import UsersCommandorsManager


router = APIRouter(
    prefix="/api"
)

@router.post("/add_some_random_command")
async def post_all_active_connections(response: Response, commandor_id:int=0):
    commandor = UsersCommandorsManager().get_commandor_by_id(id=commandor_id)
    print(commandor, UsersCommandorsManager().commandors)
    if(commandor):
        commandor.priority_commands_queue.put(
            ChooseBilet(random.randint(0, 39))
        )
        response.status_code=status.HTTP_200_OK
    else:
        response.status_code=status.HTTP_400_BAD_REQUEST
    pass

@router.get("/get_all_active_connections")
async def get_all_active_connections():
    commandors = UsersCommandorsManager().commandors
    result = {"ids":[commandor.id for commandor in commandors]}
    return JSONResponse(content=result)

@router.post("/run_webdriver")
async def run_webdriver(response: Response, commandor_id:int=0):
    commandor = UsersCommandorsManager().get_commandor_by_id(id=commandor_id)
    if(commandor):
        commandor.priority_commands_queue.put(
            RunDriver()
        )
        response.status_code=status.HTTP_200_OK
    else:
        response.status_code=status.HTTP_400_BAD_REQUEST

@router.post("/init_webdriver")
async def init_webdriver(response: Response, commandor_id:int=0):
    commandor = UsersCommandorsManager().get_commandor_by_id(id=commandor_id)
    if(commandor):
        commandor.priority_commands_queue.put(
            InitDriver(start_url='https://pdd-exam.ru')
        )
        response.status_code=status.HTTP_200_OK
    else:
        response.status_code=status.HTTP_400_BAD_REQUEST

@router.post("/shutdown_webdriver")
async def shutdown_webdriver(response: Response, commandor_id:int=0):
    commandor = UsersCommandorsManager().get_commandor_by_id(id=commandor_id)
    if(commandor):
        commandor.priority_commands_queue.put(
            ShutdownDriver()
        )
        response.status_code=status.HTTP_200_OK
    else:
        response.status_code=status.HTTP_400_BAD_REQUEST





@router.websocket("/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket
):
    await websocket.accept()
    print("session accepted")
    target_knowledge = Knowledge.get_zero_knowledge()
    commands_generator = None
    id =random.randint(0, 0)
    commandor = UsersCommandorsManager().init_new_commandor(
            id = id,
          websocket = websocket,
          commands_generator = None)
    # Начали прослушивание. 
    await commandor.start()

    UsersCommandorsManager().remove_commandor(commandor)


@router.post("/fill_randomly_bilet")
async def shutdown_webdriver(response: Response, commandor_id:int=0, bilet_id:int=0):
    commandor = UsersCommandorsManager().get_commandor_by_id(id=commandor_id)
    if(commandor):
        knowledge = Knowledge()
        for i in range(0, 20):
            knowledge.data[bilet_id][i] = random.randint(0, 3)
        
        await commandor.set_target_knowledge(knowledge=knowledge)
        response.status_code=status.HTTP_200_OK
    else:
        response.status_code=status.HTTP_400_BAD_REQUEST