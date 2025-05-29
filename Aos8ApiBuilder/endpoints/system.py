from helper import parse_system_output_json
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class SystemEndpoint(BaseEndpoint):
    def list(self):
        response = self._client.get("/cli/aos?cmd=show+system")
        if response.output:
            response.output = parse_system_output_json(response.output)
        return response


