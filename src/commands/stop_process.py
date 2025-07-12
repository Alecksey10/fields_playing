from src.commands.command_base import CommandBase


class StopProcess(CommandBase):
    command_id = 10
    def __init__(self):
        super().__init__()
    
    def to_dict(self):
        return {}
        
    @classmethod
    def from_dict(self, dct):
        return StopProcess()