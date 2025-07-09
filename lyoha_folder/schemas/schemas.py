from typing import Literal
from pydantic import BaseModel

from commands.bilet_commands.choose_bilet import ChooseBilet

class Message(BaseModel):    
    '''
    data - данные, соответствующие команде. 
    '''
    status:Literal['command', 'error', 'stop', 'terminate', 'skip', 'success']
    data:str

class DefaultCommand(BaseModel):    
    '''
    command_id: у каждой команды есть свой id.
    '''

    status:Literal['command', 'error']
    #TODO как-нибудь не в ручную хардкодить идентификаторы
    command_id:Literal[1,2,3,4,5,6,
                       7,8,9,10,11,12,13]
    json_str_command:str

if __name__=="__main__":
    command = ChooseBilet(10)
    command = DefaultCommand()