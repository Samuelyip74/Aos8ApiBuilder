from helper import parse_output_json
from endpoints.base import BaseEndpoint
from models import ApiResult

class CLIEndpoint(BaseEndpoint):
    """Endpoint for sending CLI commands to the switch."""

    def sendCommand(self,cmd:str):
        """
        Send CLI command to omniswitch.

        Returns:
            ApiResult of the CLI command.
        
        """
        response = self._client.get(f"/cli/aos?cmd={cmd.replace(" ", "+")}")       
        return response