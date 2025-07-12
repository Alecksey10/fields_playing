import asyncio
import json
from threading import Thread
import sys
import time
import traceback
from typing import Tuple

from src.executor.logger import logger
from src.schemas.schemas import ExecutorCommandResult
sys.path.append('.')
from src.commands.bilet_commands.answer_question import AnswerQuestion
from src.commands.bilet_commands.choose_question import ChooseQuestion
from src.commands.init_driver import InitDriver
from src.commands.shutdown_driver import ShutdownDriver
from src.executor.driver.driver import Driver
from src.commands.bilet_commands.choose_bilet import ChooseBilet
from src.commands.command_base import CommandBase
from src.commands.run_driver import RunDriver
from src.executor.connection.executor_api_base import ExecutorAPIBase
from src.executor.connection.executor_api_threaded_base import ExecutorAPIThreadedBase
from queue import Queue
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver   
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time

class HardcoreCommandsExecutor(ExecutorAPIThreadedBase):
    '''
    
    command_queue = Queue() : Для внутренней передачи аргументов в поток
    result_queue = Queue() : Для внутренней передачи аргументов из потока
    '''
    def __init__(self):
        self.webdriver = None
        self.__command_queue = Queue()
        self.__result_queue = Queue()
        self.is_running = False
        self.pdd_url = 'https://pdd-exam.ru'
        self.pdd_bilets_url = 'https://pdd-exam.ru/bilet/'
        self.current_bilet = -1
        self.current_question = -1

        with open('./correct_answers.json', 'r') as file:
            self.answers = json.load(file)
        
        self.is_running = True
        self.thread = Thread(target=self._run_loop)
        self.thread.start()
    
    async def execute_command(self, command:CommandBase) -> ExecutorCommandResult:
        #Реализовать команды, хардкор
        logger.debug(f"executing command {command}")
        method = None
        args = []
        kwargs = {}

        if(isinstance(command, RunDriver)):
            method = self.__run_driver
            args = [command]
        elif(isinstance(command, InitDriver)):
            method = self.__init_driver
            args = [command]
        elif(isinstance(command, ShutdownDriver)):
            method = self.__shutdown_driver
            args = [command]
        elif(isinstance(command, ChooseBilet)):
            method = self.__select_bilet_pipeline
            args = [command]
        elif(isinstance(command, ChooseQuestion)):
            method = self.__select_question
            args = [command]
        elif(isinstance(command, AnswerQuestion)):
            method = self.__answer_to_question
            args = [command]
        else:
            raise Exception("there is no implementation for such command")

        self.__command_queue.put((method, args, kwargs))
        logger.debug('1')
        while self.__result_queue.empty() and self.is_running:
            await asyncio.sleep(0.1)
        logger.debug('2')
        logger.debug(f'3, {self.is_running}')
        if not (self.__result_queue.empty()):
            res = self.__result_queue.get()
            return res
        # time.sleep(1)

    def _run_loop(self):
        """Основной цикл выполнения команд в потоке."""
        while self.is_running:
            command, args, kwargs = self.__command_queue.get()
            try:
                result = command(*args, **kwargs)
                self.__result_queue.put(ExecutorCommandResult(sucess=True, result=result))
            except Exception as ex:
                logger.debug("some exeption" + str(ex))
                logger.debug(traceback.format_exc())
                self.__result_queue.put(ExecutorCommandResult(sucess=False, result=None))
            # time.sleep(1)

    def __run_driver(self, command):
        logger.debug("driver runned")
        self.webdriver = Driver()
        self.webdriver.start()
    
    def __init_driver(self, command:InitDriver):
        self.webdriver.driver.get(command.start_url)
        pass
    
    def __select_bilet_pipeline(self, command:ChooseBilet):
        '''
        Полный pipeline выбора билета
        '''
        def select_bilet_by_number(driver, id):
            ''' важно находиться на странице с билетами'''
            elems = driver.find_elements(By.CLASS_NAME, 'pdd-online__choice-link')
            elems[id].click()

        if(self.webdriver.driver.current_url!=self.pdd_bilets_url):
            self.webdriver.driver.get(self.pdd_bilets_url)
            time.sleep(2)
        self.webdriver.driver.refresh()
        select_bilet_by_number(self.webdriver.driver, command.bilet_number)
        time.sleep(1)
        self.webdriver.driver.refresh()
        #И такой костыль, чтобы избавиться от рекламы...
        self.current_bilet = command.bilet_number
    
    def __select_question(self, command:ChooseQuestion):
        '''Важно находиться на желанном билете'''
        elems = self.webdriver.driver.find_elements(By.CLASS_NAME, 'bilet__qs-num-item')
        elems[command.question_number].click()
        #Игнорируем то, что при ответе на вопрос меняется текущий вопрос (в случае успешного ответа)
        self.current_question = command.question_number

    

    def __answer_to_question(self,  command:AnswerQuestion):
        '''
        Важно находиться на желанном билете и вопросе
        '''
        logger.debug("answering to question")
        def format_text(string:str):
            return string.replace(',','').replace('.','').lower()
                
        try:
            correct_answer_text = format_text(self.answers[str(self.current_bilet)][self.current_question])
            logger.debug(correct_answer_text)

            answers_buttons = self.webdriver.driver.find_elements(By.CLASS_NAME, 'bilet__answer-btn')
            flag = False
            logger.debug(f"buttons count: {len(answers_buttons)}")
            for answer_btn in answers_buttons:
                text = answer_btn.get_attribute('innerText')
                text = format_text(text)
                if(command.answer_type):
                    if(text==correct_answer_text):
                        answer_btn.click()
                        flag = True
                        break
                else:
                    if(text!=correct_answer_text):
                        answer_btn.click()
                        flag = True
                        break
            time.sleep(1)
            if(not flag):
                raise Exception(f"answer was not founded, {self.current_bilet} ,{self.current_question} ,{command.answer_type}")
            
        except Exception as ex:
            logger.debug(f"{command}")
            raise ex

    def __shutdown_driver(self, command):
        logger.debug("shutdown")
        self.webdriver.shutdown()
        logger.debug("shutdowned")
        pass
    


async def main():
    
    handler = HardcoreCommandsExecutor()
    handler.start()
    print(await handler.execute_command(command=RunDriver()))
    await asyncio.sleep(10)
    print(await handler.execute_command(command=InitDriver('https://yandex.ru')))
    await asyncio.sleep(3)
    print(await handler.execute_command(command=ShutdownDriver()))
    await asyncio.sleep(3)


if __name__=="__main__":
    asyncio.run(main())