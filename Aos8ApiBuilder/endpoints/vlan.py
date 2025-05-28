from endpoints.base import BaseEndpoint
from models import ApiResult

class VlanEndpoint(BaseEndpoint):
    def list(self):
        response = self._client.get("/?domain=mib&urn=vlanTable")
        result = response.json()
        if "result" not in result or result["result"].get("diag") != 200:
            raise Exception("Failed to retrieve VLAN list")
        return result["result"]["data"]

    def create_vlan(self, vlan_id: int, description: str) -> ApiResult:
        payload = {
            "mibObject0": f"vlanNumber:{vlan_id}",
            "mibObject1": f"vlanDescription:{description}"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return self._client.post("/?domain=mib&urn=vlanTable", data=payload, headers=headers)
    
    def delete_vlan(self, vlan_id: int) -> ApiResult:
        payload = {
            "mibObject0": f"vlanNumber:{vlan_id}",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return self._client.delete("/?domain=mib&urn=vlanTable", data=payload, headers=headers)
