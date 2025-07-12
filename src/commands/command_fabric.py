import json
import sys

sys.path.append('.')
from src.commands.command_base import CommandBase
from src.schemas.schemas import DefaultCommand

from src.commands.command_register import CommandRegister


class CommandFabric():
    '''Фабрика для команд'''
    def command_from_id(id, **kwargs) -> CommandBase:
        '''создаём команду на основе её уникального иденитфикатора'''
        registered_classes = CommandRegister.get_registered_classes()
        for key, reg_class in registered_classes.items():
            if(reg_class.command_id==id):
                return reg_class.from_dict(kwargs)
        raise Exception("there is no such command")




def main():
    from src.commands.bilet_commands.choose_bilet import ChooseBilet
    from src.commands.init_driver import AnswerQuestion
    #Вариант 1
    cb = ChooseBilet(12)
    msg = DefaultCommand(
        status='command',
        command_id=cb.command_id,
        json_str_command=json.dumps(cb.to_dict())
    )
    print(msg)
    cb2:CommandBase = CommandFabric.command_from_id(msg.command_id,
                                        **json.loads(msg.json_str_command)
                                        )
    print(cb2, cb2.to_dict())

    print(CommandRegister.get_registered_classes())
    # Вариант 2
    aq = AnswerQuestion(False)
    msg = DefaultCommand(
        status='command',
        command_id=aq.command_id,
        json_str_command=json.dumps(aq.to_dict())
    )
    print(msg)
    aq2:CommandBase = CommandFabric.command_from_id(msg.command_id,
                                        **json.loads(msg.json_str_command)
                                        )
    print(aq2, aq2.to_dict())

    print(CommandRegister.get_registered_classes())

if __name__=="__main__":
    main()
    pass