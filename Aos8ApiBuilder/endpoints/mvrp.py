from helper import parse_output_json
from endpoints.base import BaseEndpoint
from models import ApiResult

class MvrpEndpoint(BaseEndpoint):
    """Endpoint for managing MVRP configuration."""

    def globalMVRP(self) -> ApiResult:
        """
        Retrieve global MVRP configuration settings.

        Returns:
            ApiResult: MVRP global status and VLAN limit configuration.
        """
        params = {
            "domain": "mib",
            "urn": "alcatelIND1MVRPMIBObjects",
            "mibObject0": "alaMvrpGlobalStatus",
            "mibObject1": "alaMvrpMaxVlanLimit"
        }

        response = self._client.get("/", params=params)
        return response
    
    def mvrpPortConfig(self, limit: int = 200) -> ApiResult:
        """
        Retrieve MVRP port configuration table.

        Args:
            limit (int): Maximum number of rows to return (default is 200).

        Returns:
            ApiResult: The MVRP port configuration per interface.
        """
        params = {
            "domain": "mib",
            "urn": "alaMvrpPortConfigTable",
            "mibObject0": "alaMvrpPortConfigIfIndex",
            "mibObject1": "alaMvrpPortStatus",
            "mibObject2": "alaMvrpPortConfigRegistrarMode",
            "mibObject3": "alaMvrpPortConfigApplicantMode",
            "mibObject4": "alaMvrpPortConfigJoinTimer",
            "mibObject5": "alaMvrpPortConfigLeaveTimer",
            "mibObject6": "alaMvrpPortConfigLeaveAllTimer",
            "mibObject7": "alaMvrpPortConfigPeriodicTimer",
            "mibObject8": "alaMvrpPortConfigPeriodicTransmissionStatus",
            "function": "slotPort_ifindex",
            "object": "alaMvrpPortConfigIfIndex",
            "limit": str(limit),
            "ignoreError": "true"
        }

        response = self._client.get("/", params=params)
        return response    