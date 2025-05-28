from endpoints.base import BaseEndpoint


class VlanEndpoint(BaseEndpoint):
    def list(self):
        """List all VLANs."""
        url = "?domain=mib&urn=vlanTable"
        response = self._client.get(url)
        result = response.json()
        if "result" not in result or result["result"].get("diag") != 200:
            raise Exception("Failed to retrieve VLAN list")
        return result["result"]["data"]

    def create_vlan(self, vlan_id: int, description: str):
        """Create a new VLAN using MIB interface."""
        url = "?domain=mib&urn=vlanTable"
        payload = {
            "mibObject0": f"vlanNumber:{vlan_id}",
            "mibObject1": f"vlanDescription:{description}"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = self._client.post(url, data=payload, headers=headers)
        result = response.json()
        if "result" not in result or result["result"].get("diag") != 200:
            raise Exception("VLAN creation failed: " + str(result["result"].get("error")))
        return result
