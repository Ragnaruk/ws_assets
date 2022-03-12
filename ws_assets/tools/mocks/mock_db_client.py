from typing import List, Optional

from ws_assets.tools.meta.base_client import BaseClient


class MockDBClient:
    """
    Class that mocks `open`, `close`, `fetchone`, and `fetchall` methods.

    Used for testing.
    """

    def __init__(self, return_fetchall: Optional[List[dict]] = None):
        self.return_fetchall: Optional[List[dict]] = return_fetchall

    async def fetchall(self, *args, **kwargs):
        return self.return_fetchall
