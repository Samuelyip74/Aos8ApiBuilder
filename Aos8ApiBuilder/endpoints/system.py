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

    def set_name(self, name: str) -> ApiResult:
        name_quoted = f'"{name}"'
        response = self._client.get(f"/cli/aos?cmd=system+name+{name_quoted}")
        if response.success:
            return self.list()
        return response

    def set_contact(self, contact: str) -> ApiResult:
        contact_quoted = f'"{contact}"'
        response = self._client.get(f"/cli/aos?cmd=system+contact+{contact_quoted}")
        if response.success:
            return self.list()
        return response

    def set_location(self, location: str) -> ApiResult:
        location_quoted = f'"{location}"'
        response = self._client.get(f"/cli/aos?cmd=system+location+{location_quoted}")
        if response.success:
            return self.list()
        return response
    
    def set_date(self, data: str) -> ApiResult:
        date_quoted = f'"{data}"'
        response = self._client.get(f"/cli/aos?cmd=system+date+{date_quoted}")
        if response.success:
            return self.list()
        return response 

    def set_time(self, time: str) -> ApiResult:
        time_quoted = f'"{time}"'
        response = self._client.get(f"/cli/aos?cmd=system+time+{time_quoted}")
        if response.success:
            return self.list()
        return response    

    def set_timezone(self, timezone: str) -> ApiResult:
        timezone_quoted = f'"{timezone}"'
        response = self._client.get(f"/cli/aos?cmd=system+timezone+{timezone_quoted}")
        if response.success:
            return self.list()
        return response