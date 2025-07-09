from abc import ABC

from commands.command_register import CommandRegister

class CommandBase(metaclass=CommandRegister):
    command_id = -1
    def __init__(self):
        super().__init__()
    
    def to_dict(self):
        raise Exception("not implemented")

    @classmethod
    def from_dict(self, dct):
        raise Exception("not implemented")