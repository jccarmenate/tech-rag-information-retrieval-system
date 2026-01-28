from abc import ABC, abstractmethod

import httpx

from app.acquisition.schemas import RawDocument


class BaseConnector(ABC):
    """A connector fetches recent documents from one external data source.

    Subclasses only need to implement `fetch`; the HTTP client and its
    lifecycle are handled here so every connector shares the same timeout,
    user agent and error-handling behaviour.
    """

    source_name: str = "base"
    timeout_seconds: float = 15.0

    def __init__(self) -> None:
        self._client = httpx.Client(
            timeout=self.timeout_seconds,
            headers={"User-Agent": "CodeRadar/0.1 (+https://github.com/JuanCMath)"},
        )

    def __enter__(self) -> "BaseConnector":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._client.close()

    def _get_json(self, url: str, **kwargs: object) -> dict | list:
        response = self._client.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    @abstractmethod
    def fetch(self, limit: int = 20) -> list[RawDocument]:
        """Return up to `limit` normalized documents fetched from the source."""
        raise NotImplementedError
