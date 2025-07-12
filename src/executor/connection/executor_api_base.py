from abc import ABC, abstractmethod
from selenium import webdriver

from src.commands.command_base import CommandBase
from src.schemas.schemas import ExecutorCommandResult


class ExecutorAPIBase(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    async def execute_command(command: CommandBase) -> ExecutorCommandResult:
        pass