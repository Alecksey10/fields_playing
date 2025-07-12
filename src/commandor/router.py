import json
from fastapi import APIRouter, Depends, Response
import random
from typing import Annotated, Dict
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
from pydantic import BaseModel, Field

from src.commandor.dependencies import CommandorDep, commandor
from src.commandor.user_commandor import UserCommandor
from src.commands.init_driver import InitDriver
from src.commands.run_driver import RunDriver
from src.commands.shutdown_driver import ShutdownDriver


sys.path.append('.')
from src.commands.bilet_commands.choose_bilet import ChooseBilet
from src.commandor.knowledge.knowledge import Knowledge
from src.commandor.commands_generator import CommandsGenerator
from src.commandor.users_commandor_manager import UsersCommandorsManager


router = APIRouter(
    prefix="/api"
)

@router.post("/add_some_random_command")
async def post_all_active_connections(response: Response, commandor:CommandorDep):
    '''Команда на выбор случайного билета'''
    commandor.priority_commands_queue.put(
        ChooseBilet(random.randint(0, 39))
    )

@router.get("/get_all_active_connections")
async def get_all_active_connections():
    '''Получение идентификаторов всех управляющих объектов commandors'''
    commandors = UsersCommandorsManager().commandors
    result = {"ids":[commandor.id for commandor in commandors]}
    return JSONResponse(content=result)

@router.post("/run_webdriver")
async def run_webdriver(response: Response, commandor:CommandorDep):
    '''Отправка команды на запуск webdriver (по идее API должен быть доступен для тех executor'ов, которые основаны на эмуляции браузера (selenium в моём случае))'''
    print(commandor)
    commandor.priority_commands_queue.put(
        RunDriver()
    )


@router.post("/init_webdriver")
async def init_webdriver(response: Response, commandor:CommandorDep):
    '''Инициализация драйвера, пока ничего не делает'''
    commandor.priority_commands_queue.put(
        InitDriver(start_url='https://pdd-exam.ru'))
    
@router.post("/shutdown_webdriver")
async def shutdown_webdriver(response: Response, commandor:CommandorDep):
    '''Выключение драйвера'''
    commandor.priority_commands_queue.put(
        ShutdownDriver()
    )

@router.post("/fill_current_knowledge")
async def fill_current_knowledge(response: Response, commandor:CommandorDep, value:int=-2):
    '''Заполняем сведения о текущем состоянии билета некоторым значением.
    Не следует делать это во время выполнения, так как commands generator начнёт в случае чего делать всё сначала
    '''
    commandor.last_success_knowledge._fill_const(value=value)
    
    # await commandor.commands_generator.update_current_knowledge()

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

@router.post("/init_by_last_correct_knowledge")
async def init_by_last_correct_knowledge(response: Response, commandor:CommandorDep):
    
    with open("./last_correct_knowledge.json", mode="r") as file:
        dct  =json.load(file)
        last_knowledge = Knowledge.from_dict(dct['current'])
        last_target_knowledge = Knowledge.from_dict(dct['target'])
        response.status_code=status.HTTP_200_OK
        await commandor.set_target_knowledge(knowledge=last_target_knowledge, start_knowledge=last_knowledge)

from random import choice, randint


class LabyrinthParams(BaseModel):
    width: int = Field(ge=1, le=39,default=39)
    height: int = Field(ge=1, le=19,default=19)
    
@router.post("/fill_by_labyrinth")
async def fill_by_labyrinth(response: Response, commandor:CommandorDep, lab_params:LabyrinthParams):
    height=lab_params.height
    width=lab_params.width
    wall_value = 1
    # 1. Создаём сетку (1 = стена, 0 = путь)
    maze = []
    for i in range(0, height):
        maze.append([])
        for j in range(0, width):
            maze[-1].append(wall_value)
    
    # 2. Алгоритм генерации (модифицированный Prim)
    stack = [(1, 1)]
    maze[1][1] = 0
    
    while stack:
        x, y = stack[-1]
        directions = []
        
        # Проверяем возможные направления
        if x > 2 and maze[y][x-2] == wall_value:
            directions.append((-2, 0))
        if x < width-3 and maze[y][x+2] == wall_value:
            directions.append((2, 0))
        if y > 2 and maze[y-2][ x] == wall_value:
            directions.append((0, -2))
        if y < height-3 and maze[y+2][ x] == wall_value:
            directions.append((0, 2))
        
        if directions:
            dx, dy = choice(directions)
            maze[y + dy][ x + dx] = 0
            maze[y + dy//2][x + dx//2] = 0
            stack.append((x + dx, y + dy))
        else:
            stack.pop()
    
    # 3. Добавляем вход и выход
    maze[1][0] = 2  # Старт
    maze[height-2][width-1] = 2  # Финиш
    
    knowledge = Knowledge()
    knowledge._fill_zero()
    for i in range(0, width):
        for j in range(0, height):
            knowledge.data[i][j] = maze[j][i]
    [print(m) for m in maze]
    [print(m[1]) for m in knowledge.data.items()]
    await commandor.set_target_knowledge(knowledge=knowledge)



@router.post("/fill_randomly_bilet")
async def shutdown_webdriver(response: Response, commandor:CommandorDep, bilet_id:int=0):

    knowledge = Knowledge()
    for i in range(0, 20):
        knowledge.data[bilet_id][i] = random.randint(0, 3)
    
    await commandor.set_target_knowledge(knowledge=knowledge)


