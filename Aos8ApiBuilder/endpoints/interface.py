from helper import parse_interface_status, parse_interface_detail
from typing import Optional,List, Dict
from endpoints.base import BaseEndpoint
from models import ApiResult

class InterfaceEndpoint(BaseEndpoint):

    def _expand_port_range(self, port_range: str) -> list[str]:
        if '-' not in port_range:
            return [port_range]
        
        prefix, start_end = port_range.rsplit('/', 1)
        start, end = map(int, start_end.split('-'))
        return [f"{prefix}/{i}" for i in range(start, end + 1)]

    def list(self):
        response = self._client.get("/cli/aos?cmd=show+interfaces+status")
        if response.output:
            response.output = parse_interface_status(response.output)
        return response

    def get_interface(self, port:str):
        response = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{port}")
        if response.success:
            return parse_interface_detail(response.output)
        return None

    def set_interface(self, port: str, parameter: str, value: str) -> ApiResult:
        """
        Set admin-state, autoneg, or epp on a given port or range,
        and return the updated interface status as a list of parsed results.

        :param port: e.g., "1/1/1" or "1/1/1-3"
        :param parameter: "admin-state", "autoneg", or "epp"
        :param value: "enable" or "disable"
        :return: List of parsed interface details (one per port)
        """
        if parameter not in {"admin-state", "autoneg", "epp"}:
            raise ValueError("Invalid parameter: choose from 'admin-state', 'autoneg', or 'epp'")
        if value not in {"enable", "disable"}:
            raise ValueError("Invalid value: choose from 'enable' or 'disable'")

        # 1. Send the config command
        cmd = f"interfaces+port+{port}+{parameter}+{value}"
        response = self._client.get(f"/cli/aos?cmd={cmd}")

        # 2. Build list of ports affected
        affected_ports = self._expand_port_range(port)

        # 3. Fetch and parse the status for each affected port
        parsed_results = []
        for p in affected_ports:
            show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
            if show_resp.success:
                parsed = parse_interface_detail(show_resp.output)
                parsed_results.append(parsed)
        response.output = parsed_results
        return response

    def enable(self, port: str) -> ApiResult:
        return self.set_interface(port, "admin-state", "enable")

    def disable(self, port: str) -> ApiResult:
        return self.set_interface(port, "admin-state", "disable")

    def autoneg_enable(self, port: str) -> ApiResult:
        return self.set_interface(port, "autoneg", "enable")

    def autoneg_disable(self, port: str) -> ApiResult:
        return self.set_interface(port, "autoneg", "disable")

    def epp_enable(self, port: str) -> ApiResult:
        return self.set_interface(port, "epp", "enable")

    def epp_disable(self, port: str) -> ApiResult:
        return self.set_interface(port, "epp", "disable")
