from abc import ABC, abstractmethod
import threading
from selenium import webdriver

from src.commands.command_base import CommandBase
from src.executor.connection.executor_api_base import ExecutorAPIBase


class ExecutorAPIThreadedBase(ExecutorAPIBase):
    '''
    Для обёртки логики через отдельный поток. (Не увидел, 
    поддерживает ли Selenium асинхронное программирование, 
    поэтому буду его через поток делать с асинхронным интерфейсом)
    '''
    def __init__(self):
        super().__init__()
        
    @abstractmethod
    def _run_loop(self):
        pass