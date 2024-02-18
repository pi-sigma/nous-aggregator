class MockResponse:
    def __init__(self, status_code: int | None = None, text: str = ""):
        self.status_code = status_code or 200
        self._text = text

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass
