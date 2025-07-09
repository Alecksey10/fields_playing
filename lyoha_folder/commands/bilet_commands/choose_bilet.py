from commands.command_base import CommandBase


class ChooseBilet(CommandBase):
    command_id = 1
    def __init__(self, bilet_number:int):
        self.bilet_number = bilet_number
        super().__init__()
    
    def to_dict(self):
        return {"bilet_number":self.bilet_number}
        
    @classmethod
    def from_dict(self, dct):
        return ChooseBilet(bilet_number=dct.get('bilet_number'))
