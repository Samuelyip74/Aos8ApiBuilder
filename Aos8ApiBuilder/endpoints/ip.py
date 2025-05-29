from helper import parse_ip_interface_output
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class IPInterfaceEndpoint(BaseEndpoint):
    def list(self):
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
        admin_state: Optional[str] = None,  # 'enable' or 'disable'
        vlan: Optional[int] = None,
        service: Optional[int] = None,
        forward: Optional[bool] = None,
        local_proxy_arp: Optional[bool] = None,
        encapsulation: Optional[str] = None,  # 'e2' or 'snap'
        primary: Optional[bool] = None
    ) -> ApiResult:

        cmd = f"ip+interface+{if_name}"

        if address:
            cmd += f"+address+{address}"
        if vip_address:
            cmd += f"+vip-address+{vip_address}"
        if mask:
            cmd += f"+mask+{mask}"
        if admin_state in ("enable", "disable"):
            cmd += f"+admin-state+{admin_state}"
        if vlan:
            cmd += f"+vlan+{vlan}"
        if service:
            cmd += f"+service+{service}"
        if forward is not None:
            cmd += "+forward" if forward else "+no+forward"
        if local_proxy_arp is not None:
            cmd += "+local-proxy-arp" if local_proxy_arp else "+no+local-proxy-arp"
        if encapsulation in ("e2", "snap"):
            cmd += f"+{encapsulation}"
        if primary is not None:
            cmd += "+primary" if primary else "+no+primary"

        response = self._client.get(f"/cli/aos?cmd={cmd}")
        if response.success:
            return self.list()
        return response
    
    def edit(
        self,
        if_name: str,
        address: Optional[str] = None,
        vip_address: Optional[str] = None,
        mask: Optional[str] = None,
        admin_state: Optional[str] = None,  # 'enable' or 'disable'
        vlan: Optional[int] = None,
        service: Optional[int] = None,
        forward: Optional[bool] = None,
        local_proxy_arp: Optional[bool] = None,
        encapsulation: Optional[str] = None,  # 'e2' or 'snap'
        primary: Optional[bool] = None
    ) -> ApiResult:

        cmd = f"ip+interface+{if_name}"

        if address:
            cmd += f"+address+{address}"
        if vip_address:
            cmd += f"+vip-address+{vip_address}"
        if mask:
            cmd += f"+mask+{mask}"
        if admin_state in ("enable", "disable"):
            cmd += f"+admin-state+{admin_state}"
        if vlan:
            cmd += f"+vlan+{vlan}"
        if service:
            cmd += f"+service+{service}"
        if forward is not None:
            cmd += "+forward" if forward else "+no+forward"
        if local_proxy_arp is not None:
            cmd += "+local-proxy-arp" if local_proxy_arp else "+no+local-proxy-arp"
        if encapsulation in ("e2", "snap"):
            cmd += f"+{encapsulation}"
        if primary is not None:
            cmd += "+primary" if primary else "+no+primary"

        response = self._client.get(f"/cli/aos?cmd={cmd}")
        if response.success:
            return self.list()
        return response 

    def delete(self, if_name: str) -> ApiResult:
        cmd = f"no+ip+interface+{if_name}"
        response = self._client.get(f"/cli/aos?cmd={cmd}")
        if response.success:
            return self.list()
        return response
