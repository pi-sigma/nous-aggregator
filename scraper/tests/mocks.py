from typing import Optional


class MockResponse:
    def __init__(self, status_code: Optional[int] = 200, text: str = ""):
        self.status_code = status_code
        self._text = text

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        pass
