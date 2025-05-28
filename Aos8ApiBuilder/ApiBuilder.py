from typing import Optional
from ApiClient import AosApiClient

class AosApiClientBuilder:
    def __init__(self):
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._base_url: Optional[str] = None
        self._verify_ssl: bool = False
        self._debug: bool = False

    def setUsername(self, username: str) -> 'AosApiClientBuilder':
        self._username = username
        return self

    def setPassword(self, password: str) -> 'AosApiClientBuilder':
        self._password = password
        return self

    def setBaseUrl(self, base_url: str) -> 'AosApiClientBuilder':
        self._base_url = base_url.rstrip('/')
        return self

    def setVerifySSL(self, verify: bool) -> 'AosApiClientBuilder':
        self._verify_ssl = verify
        return self

    def setDebug(self, debug: bool) -> 'AosApiClientBuilder':
        self._debug = debug
        return self

    def build(self) -> AosApiClient:
        if not all([self._username, self._password, self._base_url]):
            raise ValueError("Username, password, and base URL must all be set")

        return AosApiClient(
            username=self._username,
            password=self._password,
            base_url=self._base_url,
            verify_ssl=self._verify_ssl,
            debug=self._debug
        )
