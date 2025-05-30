from helper import parse_ip_interface_output
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class IPInterfaceEndpoint(BaseEndpoint):
    """
    Endpoint to manage IP interfaces on an Alcatel-Lucent OmniSwitch using CLI-based API calls.
    """

    def list(self):
        """
        Retrieve a list of all configured IP interfaces.

        Returns:
            ApiResult: The result object containing parsed output of the command `show ip interface`.
        """
        response = self._client.get("/cli/aos?cmd=show+ip+interface")
        if response.output:
            response.output = parse_ip_interface_output(response.output)
        return response

    def create(
        self,
        if_name: str,
        address: Optional[str] = None,
        vip_address: Optional[str] = None,
        mask: Optional[str] = None,
        admin_state: Optional[str] = None,
        vlan: Optional[int] = None,
        service: Optional[int] = None,
        forward: Optional[bool] = None,
        local_proxy_arp: Optional[bool] = None,
        encapsulation: Optional[str] = None,
        primary: Optional[bool] = None
    ) -> ApiResult:
        """
        Create a new IP interface with specified parameters.

        Args:
            if_name (str): Name of the interface.
            address (Optional[str]): IP address.
            vip_address (Optional[str]): Virtual IP address.
            mask (Optional[str]): Subnet mask.
            admin_state (Optional[str]): Interface admin state, either 'enable' or 'disable'.
            vlan (Optional[int]): VLAN ID.
            service (Optional[int]): Associated service ID.
            forward (Optional[bool]): Enable or disable packet forwarding.
            local_proxy_arp (Optional[bool]): Enable or disable local proxy ARP.
            encapsulation (Optional[str]): Encapsulation type ('e2' or 'snap').
            primary (Optional[bool]): Set as primary interface.

        Returns:
            ApiResult: Result of the creation operation or error response.
        """
        ...

    def edit(
        self,
        if_name: str,
        address: Optional[str] = None,
        vip_address: Optional[str] = None,
        mask: Optional[str] = None,
        admin_state: Optional[str] = None,
        vlan: Optional[int] = None,
        service: Optional[int] = None,
        forward: Optional[bool] = None,
        local_proxy_arp: Optional[bool] = None,
        encapsulation: Optional[str] = None,
        primary: Optional[bool] = None
    ) -> ApiResult:
        """
        Edit an existing IP interface with updated parameters.

        Args:
            if_name (str): Name of the interface.
            address (Optional[str]): IP address.
            vip_address (Optional[str]): Virtual IP address.
            mask (Optional[str]): Subnet mask.
            admin_state (Optional[str]): Interface admin state, either 'enable' or 'disable'.
            vlan (Optional[int]): VLAN ID.
            service (Optional[int]): Associated service ID.
            forward (Optional[bool]): Enable or disable packet forwarding.
            local_proxy_arp (Optional[bool]): Enable or disable local proxy ARP.
            encapsulation (Optional[str]): Encapsulation type ('e2' or 'snap').
            primary (Optional[bool]): Set as primary interface.

        Returns:
            ApiResult: Result of the edit operation or error response.
        """
        ...

    def delete(self, if_name: str) -> ApiResult:
        """
        Delete an existing IP interface.

        Args:
            if_name (str): Name of the interface to delete.

        Returns:
            ApiResult: Result of the deletion operation or error response.
        """
        ...

