from helper import parse_ip_interface_output
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class IPInterfaceEndpoint(BaseEndpoint):
    """
    Endpoint to manage IP interfaces on an Alcatel-Lucent OmniSwitch using CLI-based API calls.
    """

    def list(self, limit: int = 200) -> ApiResult:
        """
        Retrieve all IP interfaces using MIB-based GET with full object mapping.

        Args:
            limit (int): Maximum number of entries to retrieve. Defaults to 200.

        Returns:
            dict: Dictionary of IP interface entries, keyed by ifIndex.
        """
        params = {
            "domain": "mib",
            "urn": "alaIpInterfaceTable",
            "limit": str(limit),
            "ignoreError": "true",
            "function": "slotPort_ifindex|ifindex_slotPort|chassisSlot_vcIfIndex",
            "object": "alaIpInterfacePortIfindex|alaIpInterfaceArpNiSlot,0,alaIpInterfaceArpNiChassis|ifindex_slotPort_1"
        }

        # Add all 33 MIB objects
        mib_objects = [
            "ifIndex",
            "alaIpInterfaceName",
            "alaIpInterfaceAddress",
            "alaIpInterfaceMask",
            "alaIpInterfaceBcastAddr",
            "alaIpInterfaceDeviceType",
            "alaIpInterfaceTag",
            "alaIpInterfacePortIfindex",
            "alaIpInterfaceEncap",
            "alaIpInterfaceVlanID",
            "alaIpInterfaceIpForward",
            "alaIpInterfaceAdminState",
            "alaIpInterfaceOperState",
            "alaIpInterfaceOperReason",
            "alaIpInterfaceRouterMac",
            "alaIpInterfaceDhcpStatus",
            "alaIpInterfaceLocalProxyArp",
            "alaIpInterfaceDhcpOption60String",
            "alaIpInterfaceMtu",
            "alaIpInterfaceArpNiSlot",
            "alaIpInterfaceArpNiChassis",
            "alaIpInterfaceArpCount",
            "alaIpInterfacePrimCfg",
            "alaIpInterfacePrimAct",
            "alaIpInterfaceVipAddress",
            "alaIpInterfaceTunnelSrcAddressType",
            "alaIpInterfaceTunnelSrc",
            "alaIpInterfaceTunnelDstAddressType",
            "alaIpInterfaceTunnelDst",
            "alaIpInterfaceDhcpVsiAcceptFilterString",
            "alaIpInterfaceDhcpIpRelease",
            "alaIpInterfaceDhcpIpRenew",
            "alaIpInterfaceDhcpServerPreference"
        ]

        for i, obj in enumerate(mib_objects):
            params[f"mibObject{i}"] = obj

        response = self._client.get("/", params=params)
        return response

    def create_interface(self, name: str) -> ApiResult:
        """
        Create a new IP interface with the given name.

        Args:
            name (str): The logical name of the interface (e.g., 'int-999').

        Returns:
            ApiResult: The API response.
        """
        url = "/?domain=mib&urn=alaIpItfConfigTable"

        form_data = {
            "mibObject0-T1": f"alaIpItfConfigName:{name}",
            "mibObject1-T1": "alaIpItfConfigRowStatus:4"
        }

        response = self._client.post(url, data=form_data)
        if response.success:
            response = self.list()
            return response
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

