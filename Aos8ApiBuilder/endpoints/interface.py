from helper import parse_interface_status, parse_interface_detail
from typing import Optional,List, Dict
from endpoints.base import BaseEndpoint
from models import ApiResult

class InterfaceEndpoint(BaseEndpoint):
    """
    Provides interface-related configuration and status management endpoints
    for Alcatel-Lucent OmniSwitch using AOS CLI commands via API client.
    """

    def _expand_port_range(self, port_range: str) -> list[str]:
        """
        Expand a port range string into a list of individual port identifiers.

        Args:
            port_range: A string like "1/1/1-3" or "1/1/1".

        Returns:
            A list of individual port identifiers, e.g., ["1/1/1", "1/1/2", "1/1/3"].
        """
        if '-' not in port_range:
            return [port_range]
        
        prefix, start_end = port_range.rsplit('/', 1)
        start, end = map(int, start_end.split('-'))
        return [f"{prefix}/{i}" for i in range(start, end + 1)]

    def list(self) -> ApiResult:
        """
        Retrieve the status of all interfaces.

        Returns:
            An `ApiResult` with parsed interface status list if available.
        """
        response = self._client.get("/cli/aos?cmd=show+interfaces+status")
        if response.output:
            response.output = parse_interface_status(response.output)
        return response

    def get_interface(self, port: str) -> Optional[dict]:
        """
        Retrieve detailed status of a specific port.

        Args:
            port: Port identifier string, e.g., "1/1/1".

        Returns:
            A dictionary of parsed interface details or None if the request fails.
        """
        response = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{port}")
        if response.success:
            return parse_interface_detail(response.output)
        return None

    def set_interface(self, port: str, parameter: str, value: str) -> ApiResult:
        """
        Set an interface parameter and return updated status for all affected ports.

        Args:
            port: Port or range string, e.g., "1/1/1" or "1/1/1-3".
            parameter: One of "admin-state", "autoneg", or "epp".
            value: "enable" or "disable".

        Returns:
            An `ApiResult` with a list of updated interface statuses.
        """
        if parameter not in {"admin-state", "autoneg", "epp"}:
            raise ValueError("Invalid parameter: choose from 'admin-state', 'autoneg', or 'epp'")
        if value not in {"enable", "disable"}:
            raise ValueError("Invalid value: choose from 'enable' or 'disable'")

        cmd = f"interfaces+port+{port}+{parameter}+{value}"
        response = self._client.get(f"/cli/aos?cmd={cmd}")
        if response.success:
            affected_ports = self._expand_port_range(port)
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_speed(self, target: str, speed: str) -> ApiResult:
        """
        Set the speed for one or more interfaces.

        Args:
            target: Port or range string, e.g., "1/1/1" or "1/1/1-3".
            speed: Allowed values include "10", "100", ..., "100000", "auto",
                or "max 100"/"max 1000"/etc.

        Returns:
            An `ApiResult` with updated interface status per affected port.

        Raises:
            ValueError: If the speed value is invalid.
        """
        allowed_speeds = {
            "10", "100", "1000", "2500", "10000", "40000", "100000",
            "2000", "4000", "8000", "auto",
            "max 100", "max 1000", "max 4000", "max 8000"
        }

        if speed not in allowed_speeds:
            raise ValueError(f"Invalid speed value: {speed}")

        if speed.startswith("max "):
            cmd = f"interfaces+port+{target}+speed+max+{speed.split()[1]}"
        else:
            cmd = f"interfaces+port+{target}+speed+{speed}"

        response = self._client.get(f"/cli/aos?cmd={cmd}")
        if response.success:
            affected_ports = self._expand_port_range(target)
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_alias(self, port: str, alias: str) -> ApiResult:
        """
        Set or clear the alias (description) for a single port.

        Args:
            port: A single port string (e.g., "1/1/1").
            alias: Alias string (e.g., "Uplink to Core") or empty "" to clear.

        Returns:
            An `ApiResult` with the updated interface detail.

        Raises:
            ValueError: If a port range is given (not supported by this command).
        """
        if '-' in port:
            raise ValueError("Alias can only be set on a single port, not a range.")

        # Wrap alias in quotes, even if empty (e.g., "")
        quoted_alias = f'"{alias}"'
        cmd = f"interfaces+port+{port}+alias+{quoted_alias}"

        response = self._client.get(f"/cli/aos?cmd={cmd}")
        if response.success:
            affected_ports = self._expand_port_range(port)
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_duplex(self, target: str, mode: str) -> ApiResult:
        """
        Set duplex mode for a port, port range, or slot.

        Args:
            target: Port (e.g., "1/3/1"), port range (e.g., "1/3/1-4"), or slot (e.g., "1/3").
            mode: One of "full", "half", or "auto".

        Returns:
            An `ApiResult` with updated interface status if applicable.

        Raises:
            ValueError: If duplex mode is invalid.
        """
        allowed_modes = {"full", "half", "auto"}
        if mode not in allowed_modes:
            raise ValueError(f"Invalid duplex mode: {mode}. Choose from full, half, auto.")

        # Determine if it's a port or slot command
        if '-' in target or target.count('/') == 2:
            # It's a port or port range (e.g., 1/3/1 or 1/3/1-4)
            cmd = f"interfaces+port+{target}+duplex+{mode}"
        elif target.count('/') == 1:
            # It's a slot (e.g., 1/3)
            cmd = f"interfaces+slot+{target}+duplex+{mode}"
        else:
            raise ValueError("Invalid target format. Must be port (1/1/1), port range (1/1/1-2), or slot (1/1)")

        response = self._client.get(f"/cli/aos?cmd={cmd}")
        
        if response.success and "port" in cmd:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response
    
    def set_max_frame_size(self, target: str, size: int) -> ApiResult:
        """
        Configure the maximum frame size on a port or slot.

        Args:
            target: Target slot (e.g. "1/3") or port/port-range (e.g. "1/3/1", "1/3/1-4").
            size: Frame size in bytes (valid range: 1518 to 9216).

        Returns:
            ApiResult of the CLI command.
        
        Raises:
            ValueError: If the target or size is invalid.
        """
        if not (1518 <= size <= 9216):
            raise ValueError("Frame size must be between 1518 and 9216 bytes")

        if '-' in target or target.count('/') == 2:
            # Port or port range
            cmd = f"interfaces+port+{target}+max-frame-size+{size}"
        elif target.count('/') == 1:
            # Slot-level
            cmd = f"interfaces+slot+{target}+max-frame-size+{size}"
        else:
            raise ValueError("Invalid target format. Must be port (1/3/1), port range (1/3/1-4), or slot (1/3)")

        response = self._client.get(f"/cli/aos?cmd={cmd}")
        
        if response.success and "port" in cmd:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def clear_statistics(self, target: str, stat_type: str, cli_only: bool = False) -> ApiResult:
        """
        Clear interface statistics counters (Layer 2 or TDR).

        Args:
            target: Slot (e.g., "1/3") or port/port-range (e.g., "1/3/1" or "1/3/1-4").
            stat_type: "l2-statistics" or "tdr-statistics".
            cli_only: Whether to include "cli" for l2-statistics.

        Returns:
            ApiResult of the CLI command.
        
        Raises:
            ValueError: If input is invalid.
        """
        if stat_type not in {"l2-statistics", "tdr-statistics"}:
            raise ValueError("stat_type must be 'l2-statistics' or 'tdr-statistics'")
        if stat_type == "tdr-statistics" and cli_only:
            raise ValueError("cli_only is not applicable for tdr-statistics")

        if '-' in target or target.count('/') == 2:
            # Port or port range
            base_cmd = f"clear+interfaces+port+{target}+{stat_type}"
        elif target.count('/') == 1:
            # Slot-level
            base_cmd = f"clear+interfaces+slot+{target}+{stat_type}"
        else:
            raise ValueError("Invalid target format. Must be port (1/1/1), port range (1/1/1-2), or slot (1/1)")

        if stat_type == "l2-statistics" and cli_only:
            base_cmd += "+cli"

        return self._client.get(f"/cli/aos?cmd={base_cmd}")

    def admin_enable(self, port: str) -> ApiResult:
        """
        Enable administrative state of the interface.

        Args:
            port: Port or range string.

        Returns:
            `ApiResult` with updated interface status.
        """
        return self.set_interface(port, "admin-state", "enable")

    def admin_disable(self, port: str) -> ApiResult:
        """
        Disable administrative state of the interface.

        Args:
            port: Port or range string.

        Returns:
            `ApiResult` with updated interface status.
        """
        return self.set_interface(port, "admin-state", "disable")

    def autoneg_enable(self, port: str) -> ApiResult:
        """
        Enable auto-negotiation on the interface.

        Args:
            port: Port or range string.

        Returns:
            `ApiResult` with updated interface status.
        """
        return self.set_interface(port, "autoneg", "enable")

    def autoneg_disable(self, port: str) -> ApiResult:
        """
        Disable auto-negotiation on the interface.

        Args:
            port: Port or range string.

        Returns:
            `ApiResult` with updated interface status.
        """
        return self.set_interface(port, "autoneg", "disable")

    def epp_enable(self, port: str) -> ApiResult:
        """
        Enable EPP on the interface.

        Args:
            port: Port or range string.

        Returns:
            `ApiResult` with updated interface status.
        """
        return self.set_interface(port, "epp", "enable")

    def epp_disable(self, port: str) -> ApiResult:
        """
        Disable EPP on the interface.

        Args:
            port: Port or range string.

        Returns:
            `ApiResult` with updated interface status.
        """
        return self.set_interface(port, "epp", "disable")
