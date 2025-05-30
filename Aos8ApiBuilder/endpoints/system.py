from helper import parse_system_output_json
from typing import Optional
from endpoints.base import BaseEndpoint
from models import ApiResult

class SystemEndpoint(BaseEndpoint):
    """
    Endpoint to manage system-level configuration on an Alcatel-Lucent OmniSwitch using CLI-based API commands.
    """

    def list(self):
        """
        Retrieve current system configuration including name, contact, location, time, and timezone.

        Returns:
            ApiResult: The parsed result of the `show system` command.
        """
        response = self._client.get("/cli/aos?cmd=show+system")
        if response.output:
            response.output = parse_system_output_json(response.output)
        return response

    def set_name(self, name: str) -> ApiResult:
        """
        Set the system name.

        Args:
            name (str): The desired system name.

        Returns:
            ApiResult: Result of the operation or the updated system configuration.
        """
        name_quoted = f'"{name}"'
        response = self._client.get(f"/cli/aos?cmd=system+name+{name_quoted}")
        if response.success:
            return self.list()
        return response

    def set_contact(self, contact: str) -> ApiResult:
        """
        Set the system contact information.

        Args:
            contact (str): Contact name or information string.

        Returns:
            ApiResult: Result of the operation or the updated system configuration.
        """
        contact_quoted = f'"{contact}"'
        response = self._client.get(f"/cli/aos?cmd=system+contact+{contact_quoted}")
        if response.success:
            return self.list()
        return response

    def set_location(self, location: str) -> ApiResult:
        """
        Set the system location.

        Args:
            location (str): Location string describing where the system is deployed.

        Returns:
            ApiResult: Result of the operation or the updated system configuration.
        """
        location_quoted = f'"{location}"'
        response = self._client.get(f"/cli/aos?cmd=system+location+{location_quoted}")
        if response.success:
            return self.list()
        return response

    def set_date(self, data: str) -> ApiResult:
        """
        Set the system date.

        Args:
            data (str): Date string in the required CLI format (e.g., "MM/DD/YYYY").

        Returns:
            ApiResult: Result of the operation or the updated system configuration.
        """
        date_quoted = f'"{data}"'
        response = self._client.get(f"/cli/aos?cmd=system+date+{date_quoted}")
        if response.success:
            return self.list()
        return response

    def set_time(self, time: str) -> ApiResult:
        """
        Set the system time.

        Args:
            time (str): Time string in the required CLI format (e.g., "HH:MM:SS").

        Returns:
            ApiResult: Result of the operation or the updated system configuration.
        """
        time_quoted = f'"{time}"'
        response = self._client.get(f"/cli/aos?cmd=system+time+{time_quoted}")
        if response.success:
            return self.list()
        return response

    def set_timezone(self, timezone: str) -> ApiResult:
        """
        Set the system timezone.

        Args:
            timezone (str): Timezone string (e.g., "UTC+8", "PST", "GMT+1").

        Returns:
            ApiResult: Result of the operation or the updated system configuration.
        """
        timezone_quoted = f'"{timezone}"'
        response = self._client.get(f"/cli/aos?cmd=system+timezone+{timezone_quoted}")
        if response.success:
            return self.list()
        return response
