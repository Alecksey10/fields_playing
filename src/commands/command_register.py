
import sys
from typing import List, Type

sys.path.append('.')
# from src.commands.bilet_commands.command_base import CommandBase

class CommandRegister(type):
    """Метакласс для регистрации всех унаследованных классов."""
    
    # Словарь для хранения зарегистрированных классов
    _registry = {}
    
    def __new__(cls, name, bases, namespace):
        # Создаем новый класс
        new_class = super().__new__(cls, name, bases, namespace)
        
        # Регистрируем только классы, которые не являются базовыми (имеют хотя бы один атрибут)
        # if namespace.get('__module__') != '__main__' or any(k not in namespace for k in ('__module__', '__qualname__')):
        cls._registry[name] = new_class
        return new_class
    
    @classmethod
    def get_registered_classes(cls) -> List[Type['CommandBase']]:
        """Возвращает словарь зарегистрированных классов."""
        return cls._registry

try:
    from src.commands.command_base import CommandBase
except ImportError:
    CommandBase = object 