import asyncio
from websockets.asyncio.client import connect
import sys

sys.path.append('.')
from src.executor.connection.hardcore_commands_executor import HardcoreCommandsExecutor
from src.executor.connection.connection_manager import ConnectionManager



async def main():
    async with connect("ws://localhost:8000/api/ws") as websocket:
        executor = HardcoreCommandsExecutor()
        manager = ConnectionManager(executor=executor, ws = websocket)
        await manager.start()

if __name__ == "__main__":
    asyncio.run(main())