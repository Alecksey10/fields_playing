from typing import List
from commandor.user_commandor import UserCommandor
from commandor.users_commandros_fabric import UsersCommandorsFabric
from meta.singleton import Singleton

class UsersCommandorsManager(metaclass=Singleton):
    def __init__(self):
        self.commandors:List[UserCommandor] = []
        pass

    def init_new_commandor(self, *args, **kwargs) -> UserCommandor:
        commandor = UsersCommandorsFabric.createUserCommandor(UserCommandor,*args, **kwargs)
        self.commandors.append(commandor)
        return commandor

    def get_commandor_by_id(self, id):
        for commandor in self.commandors:
            if(commandor.id==id):
                return commandor
        return None
        
    def remove_commandor(self, user_commandor:UserCommandor):
        
        self.commandors.remove(user_commandor)