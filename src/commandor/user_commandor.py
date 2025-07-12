import asyncio
import json
import traceback

import fastapi
from src.commandor.commands_generator import CommandsGenerator
from src.commandor.knowledge.knowledge import Knowledge
from src.connection_states.state_connection_closed import StateConnectionClosed
from src.connection_states.state_initialization import StateInitialization
from src.connection_states.state_initialization_receive import StateInitializationReceive
from src.connection_states.state_initialization_send import StateInitializationSend
from src.connection_states.state_receive_command_result import StateReceiveCommandResult
from src.connection_states.state_send_command import StateSendCommand
from src.connection_states.state_start import StateStart
from src.connection_states.state_stop_without_notify import StateStopWithoutNotify
from src.schemas.schemas import DefaultCommand, Message
from queue import Queue

class UserCommandor():
    '''
        Основной класс Commandor, который напрямую управляет Executor на стороне клиента. 
        содержит два основных асинхронных цикла - для read и send. Работает на основе состояний.
        Получает команду на отправку для executor из commands_generator и priority_commands_queue

        :priority_commands_queue: команды, которые будут выполняться в первую очередь 
        :commands_generator: команды, которые выполняются в последнюю очередь (они уступают в приоритете в priority_commands_queue)
    '''
    def __init__(self, id, websocket:fastapi.WebSocket, commands_generator:CommandsGenerator=None):
        self.id = id
        self.websocket = websocket
        self.priority_commands_queue = Queue()
        self.current_state = StateInitializationReceive()
        self.last_success_knowledge = Knowledge()._fill_const(value=-1)
        if(commands_generator):
            self.commands_generator = commands_generator
        else:
            self.commands_generator = None

 
    async def read_messages_loop(self):
        #TODO в целом логику считывания можно вынести в иной класс, но ладно
        try:
            while True and not isinstance(self.current_state, StateStopWithoutNotify) and not isinstance(self.current_state, StateConnectionClosed):
                message = await self.websocket.receive_text()
                message_obj = Message.model_validate_json(message)
                #TODO print на logger
                print(f"Получено: {message}")
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
                    await self.__state_initialization_send()
                elif(isinstance(self.current_state, StateSendCommand)):
                    await self.__state_send_command()
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
    
    async def update_commands_generator(self, commands_generator:CommandsGenerator):
        self.commands_generator = commands_generator
        
    async def set_target_knowledge(self, knowledge: Knowledge, start_knowledge=None):
        if(start_knowledge==None):
            start_knowledge=self.last_success_knowledge
        self.commands_generator =  CommandsGenerator(target_knowledge=knowledge, start_knowledge=start_knowledge)

    async def __state_receive_command_result(self, message_obj:Message):
        # всегда общаемся подобным
        if(message_obj.status=='success'):
            if(self.commands_generator):
                self.commands_generator.shift_last_question()
                self.last_success_knowledge = self.commands_generator.current_knowledge
            self.current_state  = StateSendCommand()
        else:
            print("last success knowledge:", self.commands_generator.current_knowledge.to_dict())
            
            with open("./last_correct_knowledge.json", mode="w") as file:
                data = {}
                data["current"] = self.commands_generator.current_knowledge.to_dict()
                data["target"] = self.commands_generator.target_knowledge.to_dict()
                json.dump(data, file)
            # self.current_state = States
            raise Exception("something goes wrong")
    async def __state_initialization_send(self):
        message_obj = Message(
            status='command',
            data=json.dumps({"test":"test from server"})
        )
        message = message_obj.model_dump_json()
        await self.websocket.send_text(message)
        print(f"Отправлено: {message}, начата задержка")
        await asyncio.sleep(2)  
        self.current_state = StateSendCommand()
    async def __state_send_command(self):
        try:
            # Узнаём, какую команду сейчас надо сделать
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
