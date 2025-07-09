from abc import ABC, abstractmethod
from selenium import webdriver

from commands.command_base import CommandBase


class ExecutorAPIBase(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    async def execute_command(command: CommandBase):
        pass