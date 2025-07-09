from commands.command_base import CommandBase


class StartBilet(CommandBase):
    command_id = 5
    def __init__(self):
        super().__init__()
    
    def to_dict(self):
        return {}
        
    @classmethod
    def from_dict(self, dct):
        return StartBilet()