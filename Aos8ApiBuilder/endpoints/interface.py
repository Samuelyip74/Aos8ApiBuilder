from helper import parse_interface_status, parse_interface_detail, parse_violation_output_to_json, parse_violation_recovery_configuration
from typing import Optional,List, Dict, Union, Literal
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

    def set_flood_limit(
        self,
        target: str,
        traffic_type: str,
        rate_mode: str,
        rate_value: Union[int, Literal["enable", "disable", "default"]],
        low_threshold: Optional[int] = None
    ) -> ApiResult:
        """
        Configure flood limit settings for broadcast, multicast, unknown unicast, or all traffic types.

        Args:
            target: Slot (e.g., "1/3") or port/port-range (e.g., "1/3/1", "1/3/1-4").
            traffic_type: One of: "bcast", "mcast", "uucast", "all".
            rate_mode: One of: "pps", "mbps", "cap%", "enable", "disable", "default".
            rate_value: The value for the selected rate_mode, or "enable"/"disable"/"default".
            low_threshold: Optional low threshold value (must be lower than rate_value, when applicable).

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If input validation fails.
        """
        valid_traffic = {"bcast", "mcast", "uucast", "all"}
        valid_modes = {"pps", "mbps", "cap%", "enable", "disable", "default"}

        if traffic_type not in valid_traffic:
            raise ValueError(f"Invalid traffic_type. Must be one of {valid_traffic}")
        if rate_mode not in valid_modes:
            raise ValueError(f"Invalid rate_mode. Must be one of {valid_modes}")
        if rate_mode in {"pps", "mbps", "cap%"} and not isinstance(rate_value, int):
            raise ValueError(f"rate_value must be int for rate_mode={rate_mode}")
        if rate_mode in {"enable", "disable", "default"} and not isinstance(rate_value, str):
            raise ValueError(f"rate_value must be 'enable', 'disable', or 'default' for mode={rate_mode}")
        if rate_mode == "cap%":
            rate_mode = "cap"

        base_cmd = (
            f"interfaces+{'port' if target.count('/') == 2 or '-' in target else 'slot'}+{target}+"
            f"flood-limit+{traffic_type}+rate+{rate_mode}+{rate_value}"
        )

        if low_threshold is not None:
            if not isinstance(low_threshold, int):
                raise ValueError("low_threshold must be an integer")
            base_cmd += f"+low-threshold+{low_threshold}"

        response = self._client.get(f"/cli/aos?cmd={base_cmd}")

        if response.success and "port" in base_cmd:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_flood_limit_action(
        self,
        target: str,
        traffic_type: Literal["bcast", "mcast", "uucast", "all"],
        action: Literal["shutdown", "trap", "default"]
    ) -> ApiResult:
        """
        Configure the action taken when flood rate limits are violated for a given traffic type.

        Args:
            target: Slot (e.g., "1/3") or port/port-range (e.g., "1/3/1", "1/3/1-4").
            traffic_type: One of: "bcast", "mcast", "uucast", "all".
            action: One of: "shutdown", "trap", "default".

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If any argument is invalid.
        """
        valid_traffic = {"bcast", "mcast", "uucast", "all"}
        valid_actions = {"shutdown", "trap", "default"}

        if traffic_type not in valid_traffic:
            raise ValueError(f"Invalid traffic_type. Must be one of {valid_traffic}")
        if action not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of {valid_actions}")

        target_type = "port" if target.count("/") == 2 or "-" in target else "slot"
        cmd = f"interfaces+{target_type}+{target}+flood-limit+{traffic_type}+action+{action}"

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
    
    def set_ingress_bandwidth(
        self,
        target: str,
        action: Union[Literal["enable", "disable"], int]
    ) -> ApiResult:
        """
        Configures ingress bandwidth settings on the specified slot or port(s).

        Args:
            target: Target slot (e.g., "1/3") or port/port-range (e.g., "1/3/1", "1/3/1-4").
            action: "enable", "disable", or an integer Mbps value.

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If invalid action value.
        """
        target_type = "port" if target.count("/") == 2 or "-" in target else "slot"

        if isinstance(action, str):
            if action not in {"enable", "disable"}:
                raise ValueError("Action must be 'enable', 'disable', or an integer Mbps value.")
            cmd = f"interfaces+{target_type}+{target}+ingress-bandwidth+{action}"
        elif isinstance(action, int):
            if not (1 <= action <= 100000):  # Example: Assume max reasonable limit
                raise ValueError("Mbps value must be a positive integer.")
            cmd = f"interfaces+{target_type}+{target}+ingress-bandwidth+mbps+{action}"
        else:
            raise ValueError("Invalid action type. Must be 'enable', 'disable', or int.")

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

    def set_link_trap(self, target: str, state: Literal["enable", "disable"]) -> ApiResult:
        """
        Enables or disables link trap messages on the specified interface(s).

        Args:
            target: Target slot (e.g., "1/3") or port/port-range (e.g., "1/2/1", "1/1/1-6").
            state: "enable" to generate trap messages when port changes state, "disable" otherwise.

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If an invalid state is provided.
        """
        if state not in {"enable", "disable"}:
            raise ValueError("State must be 'enable' or 'disable'")

        target_type = "port" if target.count("/") == 2 or "-" in target else "slot"
        cmd = f"interfaces+{target_type}+{target}+link-trap+{state}"

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

    def set_ddm_status(self, state: Literal["enable", "disable"]) -> ApiResult:
        """
        Configures the Digital Diagnostics Monitoring (DDM) administrative status.

        Args:
            state: "enable" to turn on DDM monitoring; "disable" to turn it off.

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If an invalid state is provided.
        """
        if state not in {"enable", "disable"}:
            raise ValueError("State must be 'enable' or 'disable'")

        cmd = f"interfaces+ddm+{state}"

        return self._client.get(f"/cli/aos?cmd={cmd}")

    def set_wait_to_restore(
        self,
        target: str,
        value: int,
    ) -> ApiResult:
        """
        Configures the wait-to-restore timer for the specified slot or port(s).
        This timer delays the notification of a link-up event.

        Args:
            target: The target interface scope. Accepts:
                - "slot x/y"
                - "port x/y/z"
                - "port x/y/z-a" (range)
            value: Wait-to-restore timer in seconds (0 disables the timer).

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If value is negative or target is improperly formatted.
        """
        if value < 0:
            raise ValueError("wait-to-restore value must be >= 0")

        # Normalize spacing for CLI
        target = target.replace(" ", "+")
        cmd = f"interfaces+{target}+wait-to-restore+{value}"

        response = self._client.get(f"/cli/aos?cmd={cmd}")

        if response.success:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_wait_to_shutdown(
        self,
        target: str,
        value: int,
    ) -> ApiResult:
        """
        Configures the wait-to-shutdown timer for the specified slot or port(s).
        This timer delays the notification of a link-down event.

        Args:
            target: The target interface scope. Accepts:
                - "slot x/y"
                - "port x/y/z"
                - "port x/y/z-a" (range)
            value: Wait-to-shutdown timer in seconds (0 disables the timer).

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If value is negative or target is improperly formatted.
        """
        if value < 0:
            raise ValueError("wait-to-shutdown value must be >= 0")

        # Normalize spacing for CLI
        target = target.replace(" ", "+")
        cmd = f"interfaces+{target}+wait-to-shutdown+{value}"
        
        response = self._client.get(f"/cli/aos?cmd={cmd}")

        if response.success:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_eee(
        self,
        target: str,
        state: Literal["enable", "disable"]
    ) -> ApiResult:
        """
        Enables or disables Energy Efficient Ethernet (EEE) on the specified port(s) or slot.

        Args:
            target: The interface scope. Accepts:
                - "slot x/y"
                - "port x/y/z"
                - "port x/y/z-a" (range of ports)
            state: "enable" to turn on EEE, "disable" to turn it off.

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If state is not "enable" or "disable".
        """
        if state not in {"enable", "disable"}:
            raise ValueError("State must be 'enable' or 'disable'")

        target = target.replace(" ", "+")
        cmd = f"interfaces+{target}+eee+{state}"

        response = self._client.get(f"/cli/aos?cmd={cmd}")

        if response.success:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_hybrid_mode(
        self,
        target: str,
        mode: Literal["fiber", "copper"]
    ) -> ApiResult:
        """
        Configures the mode of a combo port to either fiber or copper.

        Args:
            target: The interface scope. Accepts:
                - "slot x/y"
                - "port x/y/z"
                - "port x/y/z-a" (range of ports)
            mode: "fiber" or "copper"

        Returns:
            ApiResult from the CLI API.

        Raises:
            ValueError: If mode is not "fiber" or "copper".
        """
        if mode not in {"fiber", "copper"}:
            raise ValueError("Mode must be 'fiber' or 'copper'")

        target = target.replace(" ", "+")
        cmd = f"interfaces+{target}+hybrid-mode+{mode}"

        response = self._client.get(f"/cli/aos?cmd={cmd}")

        if response.success:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response
    
    def set_loopback(
        self,
        port: str,
        enable: bool = True
    ) -> ApiResult:
        """
        Enables or disables loopback mode for the specified front-panel port.

        Args:
            port: The front-panel port(s) in the format:
                - "port x/y/z"
                - "port x/y/z-a" (range of ports)
            enable: True to enable loopback, False to disable using the 'no' form.

        Returns:
            ApiResult from the CLI API.
        """
        port = port.replace(" ", "+")
        cmd = f"{'' if enable else 'no+'}interfaces+{port}+loopback"

        response = self._client.get(f"/cli/aos?cmd={cmd}")

        if response.success:
            affected_ports = self._expand_port_range(port) if '-' in port else [port]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+interfaces+port+{p}")
                if show_resp.success:
                    parsed = parse_interface_detail(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_portgroup_speed(
        self,
        port_group_number: int,
        slot: str,
        group_range: str,
        speed: Literal["auto", "25G", "10G"]
    ) -> ApiResult:
        """
        Configures the speed of the ports within a port group.

        Args:
            port_group_number: The port group number (e.g., 1, 2, 3...).
            slot: The chassis/slot identifier (e.g., "1/1").
            group_range: The group or group range (e.g., "1", "2-4").
            speed: The desired speed for the port group ("auto", "25G", or "10G").

        Returns:
            ApiResult from the CLI API.
        """
        cmd = f"interfaces+portgroup+port-group-number+{port_group_number}+{slot}/{group_range}+speed+{speed}"
        return self._client.get(f"/cli/aos?cmd={cmd}")

    def clear_violation(
        self,
        target: str,
        is_linkagg: bool = False
    ) -> ApiResult:
        """
        Clears all the MAC address violation logs for a specified port or link aggregate.

        Args:
            target: Port in the format 'chassis/slot/port[-port2]' or linkagg ID/range like '1-2'.
            is_linkagg: If True, clears violation for a linkagg; otherwise, clears for port(s).

        Returns:
            ApiResult from the CLI API.
        """
        if is_linkagg:
            cmd = f"clear+violation+linkagg+{target}"
        else:
            cmd = f"clear+violation+port+{target}"

        response = self._client.get(f"/cli/aos?cmd={cmd}")

        if response.success:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+violation+port+{p}")
                if show_resp.success:
                    parsed = parse_violation_output_to_json(show_resp.output)
                    parsed_results.append(parsed)
            response.output = parsed_results
        return response

    def set_violation_recovery_maximum(
        self,
        scope: Literal["global", "slot", "port"],
        value: Union[int, Literal["infinite", "default"]],
        target: Optional[str] = None
    ) -> ApiResult:
        """
        Configures the maximum number of recovery attempts for MAC address violation recovery.

        Args:
            scope: "global" applies to all ports, "slot" applies to a chassis/slot, "port" applies to a port or range.
            value: Integer (0–50), "infinite", or "default".
            target: Optional. Required for "slot" or "port". E.g., '1/1' (slot), '1/1/1', or '1/1/1-3' (ports).

        Returns:
            ApiResult from the CLI API.
        """
        if scope == "global":
            if target is not None:
                raise ValueError("Global scope should not have a target.")
            if value == "default":
                raise ValueError("Value 'default' is not allowed for global scope.")
            cmd = f"violation+recovery-maximum+{value}"
        elif scope == "slot":
            if not target:
                raise ValueError("Slot scope requires a chassis/slot target (e.g., '1/1').")
            cmd = f"violation+slot+{target}+recovery-maximum+{value}"
        elif scope == "port":
            if not target:
                raise ValueError("Port scope requires a chassis/slot/port target (e.g., '1/1/1').")
            cmd = f"violation+port+{target}+recovery-maximum+{value}"
        else:
            raise ValueError(f"Unknown scope: {scope}")

        response = self._client.get(f"/cli/aos?cmd={cmd}")

        if response.success:
            affected_ports = self._expand_port_range(target) if '-' in target else [target]
            parsed_results = []
            for p in affected_ports:
                show_resp = self._client.get(f"/cli/aos?cmd=show+violation-recovery-configuration+port+{p}")
                if show_resp.success:
                    parsed = parse_violation_recovery_configuration(show_resp.output)
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
