from abc import ABC, abstractmethod


class BaseClient(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def open(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    async def __aenter__(self):
        await self.open()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
