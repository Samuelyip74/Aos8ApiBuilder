# aos_api_client/endpoints/base.py

class BaseEndpoint:
    def __init__(self, client):
        self._client = client
