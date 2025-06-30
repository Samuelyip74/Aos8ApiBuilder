from helper import parse_ip_interface_output
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class IPInterfaceEndpoint(BaseEndpoint):
    """
    Endpoint to manage IP interfaces on an Alcatel-Lucent OmniSwitch using CLI-based API calls.
    """

    def _get_ip_ifindex(self, name: str) -> str:
        """
        Retrieves IP interface configuration using a MIB-based POST request.

        Args:
            limit (int): Maximum number of records to return (default: 200)

        Returns:
            IP Interface  - ifindex, or None if not found
        """
        response = self.list()
        rows = response.data["rows"]
        for item in rows.values():
            slot_port = item.get("alaIpInterfaceName", "")
            if slot_port == name:
                return item.get("ifIndex")
        return None

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

    def create_name_interface(self, name: str) -> ApiResult:
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

    def create_IP_Interface(
        self,
        name: str,
        address: Optional[str] = None,
        mask: Optional[str] = None,
        device: str = "Vlan",
        vlan_id: Optional[int] = None,
        local_proxy_arp: Optional[bool] = False,
        encapsulation: Optional[str] = "e2",
        primary: Optional[bool] = False
    ) -> ApiResult:
        """
        Create a new IP interface with specified parameters.

        Args:
            ifindex (str): ifindex of the interface.
            address (Optional[str]): IP address.
            mask (Optional[str]): Subnet mask.
            vlan (Optional[int]): VLAN ID.
            service (Optional[int]): Associated service ID.
            encapsulation (Optional[str]): Encapsulation type ('e2' or 'snap').
            primary (Optional[bool]): Set as primary interface.

        Returns:
            ApiResult: Result of the creation operation or error response.            
        """
        ifindex = None
        response = self.create_name_interface(name)
        if response.success:

            ifindex = self._get_ip_ifindex(name)
            url = "/?domain=mib&urn=alaIpInterfaceTable"

            encapsulation_map = {
                '1': 'e2',
                '2': 'snap'
            }
            encapsulation = encapsulation_map.get(device, '1')

            device_type_map = {
                '1': 'Vlan',
                '2': 'GRE',
                '3': 'IPIP',            
            }        
            device_type = device_type_map.get(device, '1')

            primary_config_map = {
                '0': False,
                '1': True,
            }        
            primary_config = primary_config_map.get(primary, '0')                      

            form_data = {
                "mibObject0": f"ifIndex:{ifindex}",
                "mibObject1": f"alaIpInterfaceAddress:{address}",
                "mibObject2": f"alaIpInterfaceMask:{mask}",            
                "mibObject3": f"alaIpInterfaceDeviceType:{device_type}",  
                "mibObject4": "alaIpInterfacePortIfindex:0",
                "mibObject5": f"alaIpInterfaceEncap:{encapsulation}",            
                "mibObject6": f"alaIpInterfaceIpForward:1",                        
                "mibObject8": f"alaIpInterfacePrimCfg:{primary_config}",                        
            }
                # Conditionally add VLAN ID if provided
            if vlan_id is not None:
                form_data["mibObject9"] = f"alaIpInterfaceVlanID:{str(vlan_id)}"

            if ifindex is not None:
                print(form_data)
                response = self._client.post(url, data=form_data)
                if response.success:
                    response = self.list()
                    return response
                return response
        return response

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

    def delete(self, name: str) -> ApiResult:
        """
        Delete an existing IP interface.

        Args:
            name (str): The logical name of the interface (e.g., 'int-999').

        Returns:
            ApiResult: Result of the deletion operation or error response.
        """
        url = "/?domain=mib&urn=alaIpItfConfigTable"

        form_data = {
            "mibObject0-T1": f"alaIpItfConfigName:{name}",
            "mibObject1-T1": "alaIpItfConfigRowStatus:6"
        }

        response = self._client.post(url, data=form_data)
        if response.success:
            response = self.list()
            return response
        return response

