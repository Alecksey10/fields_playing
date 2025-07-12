from src.commands.command_base import CommandBase


class StartProcess(CommandBase):
    command_id = 9
    def __init__(self):
        super().__init__()
    
    def to_dict(self):
        return {}
        
    @classmethod
    def from_dict(self, dct):
        return StartProcess()