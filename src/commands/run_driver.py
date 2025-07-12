from src.commands.command_base import CommandBase


class RunDriver(CommandBase):
    command_id = 6
    def __init__(self):
        super().__init__()
    
    def to_dict(self):
        return {}
        
    @classmethod
    def from_dict(self, dct):
        return RunDriver()