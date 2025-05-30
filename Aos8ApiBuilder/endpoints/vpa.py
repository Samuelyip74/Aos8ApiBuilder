from helper import parse_output_json
from endpoints.base import BaseEndpoint
from models import ApiResult

class VlanPortAssociation(BaseEndpoint):
    """Endpoint for managing VLAN-port associations via the AOS CLI API."""

    def list(self, vlan_id: str) -> ApiResult:
        """List all ports associated with a given VLAN.

        Args:
            vlan_id (str): The VLAN ID whose member ports are to be listed.

        Returns:
            ApiResult: API response with parsed list of port members in the VLAN.
        """
        response = self._client.get(f"/cli/aos?cmd=show+vlan+{vlan_id}+members")
        if response.success:
            response.output = parse_output_json(response.output)
        return response

    def create(self, port_id: str, vlan_id: str, mode: str = "untagged") -> ApiResult:
        """Add a port to a VLAN with the specified tagging mode.

        Args:
            port_id (str): Port identifier (e.g., "1/1").
            vlan_id (str): VLAN ID to associate with the port.
            mode (str, optional): Tagging mode for the port ("untagged" or "tagged"). Defaults to "untagged".

        Returns:
            ApiResult: API response, including updated VLAN membership if successful.
        """
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+members+port+{port_id}+{mode}")
        if response.success:
            return self.list(vlan_id)
        return response

    def edit(self, port_id: str, vlan_id: str, mode: str = "untagged") -> ApiResult:
        """Modify a port's tagging mode in a VLAN.

        Args:
            port_id (str): Port identifier.
            vlan_id (str): VLAN ID.
            mode (str, optional): New tagging mode ("untagged" or "tagged"). Defaults to "untagged".

        Returns:
            ApiResult: API response, including updated VLAN membership if successful.
        """
        response = self._client.get(f"/cli/aos?cmd=vlan+{vlan_id}+members+port+{port_id}+{mode}")
        if response.success:
            return self.list(vlan_id)
        return response

    def delete(self, port_id: str, vlan_id: str, mode: str = "untagged") -> ApiResult:
        """Remove a port from a VLAN.

        Args:
            port_id (str): Port identifier.
            vlan_id (str): VLAN ID to disassociate from the port.
            mode (str, optional): (Unused) tagging mode hint for clarity. Defaults to "untagged".

        Returns:
            ApiResult: API response, including updated VLAN membership if successful.
        """
        response = self._client.get(f"/cli/aos?cmd=no+vlan+{vlan_id}+members+port+{port_id}")
        if response.success:
            return self.list(vlan_id)
        return response
