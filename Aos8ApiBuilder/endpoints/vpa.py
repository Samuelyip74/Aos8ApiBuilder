from helper import parse_output_json
from endpoints.base import BaseEndpoint
from models import ApiResult

class VlanPortAssociation(BaseEndpoint):
    def list(self, vlan_id:str) -> ApiResult:
        response = self._client.get(f"/cli/aos?cmd=show+vlan+{vlan_id}+members")
        if response.success:
            response.output = parse_output_json(response.output)
        return response

    def create(self, port_id:str, vlan_id:str, mode:str = "untagged") -> ApiResult:
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+members+port+{port_id}+{mode}")
        if response.success:
            result = self.list()
        return result
    
    def edit(self, port_id:str, vlan_id:str, mode:str = "untagged") -> ApiResult:
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+members+port+{port_id}+{mode}")
        if response.output:
            response.output = parse_output_json(response.output)
        return response    
    
    def delete(self, port_id:str, vlan_id:str, mode:str = "untagged") -> ApiResult:
        response = self._client.get(f"/cli/aos?cmd=no+vlan+{vlan_id}+members+port+{port_id}")
        if response.output:
            response.output = parse_output_json(response.output)
        return response
