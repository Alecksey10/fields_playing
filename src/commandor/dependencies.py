from typing import Annotated
from fastapi import Depends, HTTPException
from src.commandor.user_commandor import UserCommandor
from src.commandor.users_commandor_manager import UsersCommandorsManager
from src.commands.init_driver import InitDriver


async def commandor(commandor_id:int)->UserCommandor:
    commandor = UsersCommandorsManager().get_commandor_by_id(id=commandor_id)
    if not(commandor):
        raise HTTPException(status_code=400, detail="there is no such commandor")
    return commandor

CommandorDep=Annotated[UserCommandor, Depends(commandor)]
