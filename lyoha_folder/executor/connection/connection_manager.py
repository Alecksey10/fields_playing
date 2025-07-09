import asyncio
import json
from websockets import client
import websockets
import sys


sys.path.append('.')
from commands.command_fabric import CommandFabric
from connection_states.state_connection_closed import StateConnectionClosed
from schemas.schemas import DefaultCommand, Message
from connection_states.state_receive_command import StateReceiveCommand
from connection_states.state_send_command_result import StateSendCommandResult
from connection_states.state_initialization import StateInitialization
from connection_states.state_initialization_receive import StateInitializationReceive
from connection_states.state_initialization_send import StateInitializationSend
from connection_states.state_start import StateStart
from connection_states.state_stop_without_notify import StateStopWithoutNotify
from executor.connection.executor_api_base import ExecutorAPIBase


class ConnectionManager():
    def __init__(self, executor:ExecutorAPIBase, ws:websockets.client.ClientConnection):
        
        self.current_state = StateInitializationSend()
        self.executor = executor
        self.websocket = ws 

    async def read_messages_loop(self):
        try:
            while True and not isinstance(self.current_state, StateStopWithoutNotify) and not isinstance(self.current_state, StateConnectionClosed):
                # print(f"Считывание. текущее состояние - {self.current_state}")
                try:
                    message = await self.websocket.recv()
                    message_obj = Message.model_validate_json(message)
                    if(isinstance(self.current_state, StateInitializationReceive)):
                        await self.__state_initialization_receive()
                    elif(isinstance(self.current_state, StateReceiveCommand)):
                        await self.__state_receive_command(message_obj)

                    #важная строка, иначе вечный цикл
                    await asyncio.sleep(0.1)
                except websockets.exceptions.ConnectionClosed:
                    break
        except websockets.exceptions.ConnectionClosed:
            self.current_state = StateConnectionClosed()
        finally:
            print("ConnectionManager read_messages_loop stopped")

    async def send_messages_loop(self):
        try:
            while True and not isinstance(self.current_state, StateStopWithoutNotify) and not isinstance(self.current_state, StateConnectionClosed):
                # print(f"Отправка. текущее состояние - {self.current_state}")
                if(isinstance(self.current_state, StateInitializationSend)):
                    await self.__state_initialization_send()
                elif(isinstance(self.current_state, StateSendCommandResult)):
                    await self.__state_send_command_result()

                #важная строка, иначе вечный цикл
                await asyncio.sleep(0.1)
        except websockets.exceptions.ConnectionClosed:
            self.current_state = StateConnectionClosed()
        finally:
            print("ConnectionManager send_messages_loop stopped")
            self.current_state = StateConnectionClosed()

    async def start(self):
        self.current_state = StateInitializationSend()
        self.read_task = asyncio.create_task(self.read_messages_loop())
        self.send_task = asyncio.create_task(self.send_messages_loop())
        try:
            await asyncio.gather(self.read_task, self.send_task)
        except Exception as e:
            print(f"❌ Ошибка в задачах: {e}")
        finally:
            await self.stop()

    async def stop(self):
        self.running = False
        if self.read_task:
            self.read_task.cancel()
        if self.send_task:
            self.send_task.cancel()

    async def __state_initialization_receive(self):
        self.current_state = StateReceiveCommand()
    async def __state_receive_command(self, message_obj:Message):
        # всегда общаемся подобным
        message_command_obj:DefaultCommand = DefaultCommand.model_validate_json(message_obj.data)
        print(f"command : {message_command_obj}, логика начата")
        command = CommandFabric.command_from_id(message_command_obj.command_id,
                                        **json.loads(message_command_obj.json_str_command))
        #задержка для "выполнения" логики
        await self.executor.execute_command(command)
        self.current_state = StateSendCommandResult()
    
    async def __state_initialization_send(self):
        message_obj = Message(
            status='command',
            data=json.dumps({"test":"test from client"})
        )
        message = message_obj.model_dump_json()
        await self.websocket.send(message)
        print(f"Отправлено: {message}, начата задержка")
        self.current_state = StateInitializationReceive()
        await asyncio.sleep(2)
    
    async def __state_send_command_result(self):
        message_obj = Message(
            status='success',
            data=json.dumps({"data":"command successfully done",
                             'sucess':True})
        )
        message = message_obj.model_dump_json()
        await self.websocket.send(message)
        print(f"Отправлено: {message}")
        self.current_state = StateReceiveCommand()


