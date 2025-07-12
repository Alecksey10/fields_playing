

from src.commandor.user_commandor import UserCommandor


class UsersCommandorsFabric():
    def createUserCommandor(cls_obj, *args, **kwargs) -> UserCommandor:
        return UserCommandor(*args, **kwargs)
