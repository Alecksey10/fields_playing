import asyncio
import json
import traceback

import fastapi
from commandor.commands_generator import CommandsGenerator
from commandor.knowledge.knowledge import Knowledge
from connection_states.state_connection_closed import StateConnectionClosed
from connection_states.state_initialization import StateInitialization
from connection_states.state_initialization_receive import StateInitializationReceive
from connection_states.state_initialization_send import StateInitializationSend
from connection_states.state_receive_command_result import StateReceiveCommandResult
from connection_states.state_send_command import StateSendCommand
from connection_states.state_start import StateStart
from connection_states.state_stop_without_notify import StateStopWithoutNotify
from schemas.schemas import DefaultCommand, Message
from queue import Queue

class UserCommandor():
    def __init__(self, id, websocket:fastapi.WebSocket, commands_generator:CommandsGenerator=None):
        self.id = id
        self.websocket = websocket
        self.priority_commands_queue = Queue()
        # на него будет заполняться 
        self.current_knowledge = Knowledge.get_zero_knowledge()
        self.current_state = StateInitializationReceive()
        if(commands_generator):
            self.commands_generator = commands_generator
        else:
            self.commands_generator = None

    def get_status(self)->Knowledge:
        return self.current_knowledge
    
    async def read_messages_loop(self):
        #TODO в целом логику считывания можно вынести в иной класс, но ладно
        try:
            while True and not isinstance(self.current_state, StateStopWithoutNotify) and not isinstance(self.current_state, StateConnectionClosed):
                message = await self.websocket.receive_text()
                message_obj = Message.model_validate_json(message)
                if(isinstance(self.current_state, StateInitializationReceive)):                
                    print(message)
                    self.current_state  = StateInitializationSend()
                elif(isinstance(self.current_state, StateReceiveCommandResult)):                
                    await self.__state_receive_command_result(message_obj=message_obj)
                #важная строка, иначе вечный цикл
                await asyncio.sleep(0)
        except fastapi.WebSocketDisconnect:
            self.current_state = StateConnectionClosed()
        finally:
            print("ConnectionManager read_messages_loop stopped")

    async def send_messages_loop(self):
        #TODO в целом логику взаимодействия с вебсокетом вынести в иной класс, но ладно
        try:
            while True and not isinstance(self.current_state, StateStopWithoutNotify) and not isinstance(self.current_state, StateConnectionClosed):
                if(isinstance(self.current_state, StateInitializationSend)):
                    message_obj = Message(
                        status='command',
                        data=json.dumps({"test":"test from server"})
                    )
                    message = message_obj.model_dump_json()
                    await self.websocket.send_text(message)
                    print(f"Отправлено: {message}, начата задержка")
                    await asyncio.sleep(2)  
                    self.current_state = StateSendCommand()
                elif(isinstance(self.current_state, StateSendCommand)):
                    try:
                        command = None
                        if(not self.priority_commands_queue.empty()):
                            command = self.priority_commands_queue.get()
                        elif(self.commands_generator):
                            command = (next(self.commands_generator))
                        
                        if(command):
                            message_command_obj = DefaultCommand(
                                status='command',
                                command_id=command.command_id,
                                json_str_command=json.dumps(command.to_dict())
                            )
                            message_obj = Message(
                                status='command',
                                data = message_command_obj.model_dump_json()
                            )
                            message = message_obj.model_dump_json()

                            await self.websocket.send_text(message)
                            print(f"Отправлено: {message}, начата задержка")
                            self.current_state = StateReceiveCommandResult()
                    except StopIteration:
                        print("stop iteration")
                        pass
                        # self.current_state = StateStopWithoutNotify()
                #важная строка, иначе вечный цикл
                await asyncio.sleep(0)
        except fastapi.WebSocketDisconnect:
            self.current_state = StateConnectionClosed()
        finally:
            print("ConnectionManager send_messages_loop stopped")

    async def start(self):
        self.current_state = StateInitializationReceive()
        self.read_task = asyncio.create_task(self.read_messages_loop())
        self.send_task = asyncio.create_task(self.send_messages_loop())
        try:
            await asyncio.gather(self.read_task, self.send_task)
        except Exception as e:
            print(f"❌ Ошибка в задачах: {e}, {type(e)}")
            print(traceback.format_exc())
        finally:
            await self.stop()
    
    async def stop(self):
        print("Соединение остановлено")

        # await self.websocket.close()
        return

    async def resume(self):
        raise Exception("not implemented")
    
    async def set_target_knowledge(self, knowledge: Knowledge):
        self.commands_generator =  CommandsGenerator(target_knowledge=knowledge)

    async def __state_receive_command_result(self, message_obj:Message):
        # всегда общаемся подобным
        if(message_obj.status=='success'):
            if(self.commands_generator):
                self.commands_generator.shift_last_question()
            self.current_state  = StateSendCommand()
        else:
            raise Exception("something goes wrong")
