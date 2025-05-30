from helper import parse_vlan_output_json
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class VlanEndpoint(BaseEndpoint):
    """Endpoint for managing VLAN configuration via the AOS CLI API."""

    def list(self):
        """Retrieve the list of VLANs.

        Returns:
            ApiResult: Parsed VLAN data from the switch.
        """
        response = self._client.get("/cli/aos?cmd=show+vlan")
        if response.output:
            response.output = parse_vlan_output_json(response.output)
        return response

    def create(self, vlan_id: int, description: Optional[str] = None, mtu: int = 1500) -> ApiResult:
        """Create a new VLAN with optional description and MTU.

        Args:
            vlan_id (int): VLAN ID to create.
            description (Optional[str], optional): VLAN name/description. Defaults to "VLAN_{vlan_id}".
            mtu (int, optional): MTU size for the VLAN. Defaults to 1500.

        Returns:
            ApiResult: API response, including the updated VLAN list if successful.
        """
        description = description or f"VLAN_{vlan_id}"
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+name+{description}")
        if response.success:
            response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+mtu-ip+{mtu}")
            if response.success:
                return self.list()
        return response

    def edit(self, vlan_id: int, description: Optional[str] = None, mtu: int = 1500) -> ApiResult:
        """Edit an existing VLAN's description and MTU.

        Args:
            vlan_id (int): VLAN ID to modify.
            description (Optional[str], optional): New VLAN name/description. Defaults to "VLAN_{vlan_id}".
            mtu (int, optional): Updated MTU size. Defaults to 1500.

        Returns:
            ApiResult: API response, including the updated VLAN list if successful.
        """
        description = description or f"VLAN_{vlan_id}"
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+name+{description}")
        if response.success:
            response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+mtu-ip+{mtu}")
            if response.success:
                return self.list()
        return response

    def delete(self, vlan_id: int) -> ApiResult:
        """Delete a VLAN by its ID.

        Args:
            vlan_id (int): The VLAN ID to remove.

        Returns:
            ApiResult: API response, including the updated VLAN list if successful.
        """
        response = self._client.get(f"/cli/aos?cmd=no+vlan+{vlan_id}")
        if response.success:
            return self.list()
        return response

