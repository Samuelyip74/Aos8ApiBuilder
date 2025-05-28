from helper import parse_output_json
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class VlanEndpoint(BaseEndpoint):
    def list(self):
        response = self._client.get("/cli/aos?cmd=show+vlan")
        if response.output:
            response.output = parse_output_json(response.output)
        return response

    def create(self, vlan_id: int, description: Optional[str] = None, mtu: int = 1500) -> ApiResult:
        description = description or f"VLAN_{vlan_id}"
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+name+{description}+mtu+{mtu}")
        if response.output:
            response.output = parse_output_json(response.output)
        return response
    
    def edit(self, vlan_id: int, description: Optional[str] = None, mtu: int = 1500) -> ApiResult:
        description = description or f"VLAN_{vlan_id}"
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+name+{description}+mtu+{mtu}")
        if response.output:
            response.output = parse_output_json(response.output)
        return response
    
    def delete(self, vlan_id: int) -> ApiResult:
        response = self._client.get(f"/cli/aos?cmd=no+vlan+{vlan_id}")
        if response.output:
            response.output = parse_output_json(response.output)
        return response
