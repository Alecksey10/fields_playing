from commands.command_base import CommandBase


class InitDriver(CommandBase):
    command_id = 7
    def __init__(self, start_url=""):
        self.start_url = start_url
        super().__init__()
    
    def to_dict(self):
        return {"start_url":self.start_url}
        
    @classmethod
    def from_dict(self, dct):
        return InitDriver(start_url=dct.get('start_url'))