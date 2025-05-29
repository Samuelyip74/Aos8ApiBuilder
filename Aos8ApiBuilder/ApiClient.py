import httpx
from models import ApiResult
from endpoints.vlan import VlanEndpoint
from endpoints.vpa import VlanPortAssociation
from endpoints.ip import IPInterfaceEndpoint



class AosApiClient:
    def __init__(self, username: str, password: str, base_url: str, verify_ssl: bool = False, debug: bool = False):
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self._client = httpx.Client(
            base_url=self.base_url,
            verify=verify_ssl,
            timeout=httpx.Timeout(10.0),
            headers={
                "Accept": "application/vnd.alcatellucentaos+json",
                "User-Agent": "AOSApiClient/1.0"
            }
        )
        self._login()

        self.vlan = VlanEndpoint(self)
        self.vpa = VlanPortAssociation(self)
        self.ip = IPInterfaceEndpoint(self)

    def _login(self):
        url = f"/auth/"
        params = {
            "username": self.username,
            "password": self.password,
        }
        response = self._client.get(url, params=params)
        if self.debug:
            print(f"🔐 Login response {response.status_code}: {response.text}")
        if response.status_code != 200:
            raise Exception("Login failed")
        if "wv_sess" not in self._client.cookies:
            raise Exception("Login succeeded but 'wv_sess' cookie not found")

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        if self.debug:
            print(f"➡️ {method} {path}")
            if "params" in kwargs:
                print("Params:", kwargs["params"])
            if "data" in kwargs:
                print("Form Data:", kwargs["data"])
            if "json" in kwargs:
                print("JSON:", kwargs["json"])

        response = self._client.request(method, path, **kwargs)

        if response.status_code == 401:
            print("🔁 401 Unauthorized. Re-authenticating...")
            self._login()
            response = self._client.request(method, path, **kwargs)

        if self.debug:
            print("⬅️ Response:", response.status_code, response.text)

        return self._handle_response(response)
    
    def _handle_response(self, response: httpx.Response) -> ApiResult:
        try:
            result = response.json()
        except ValueError:
            return ApiResult(success=False, diag=response.status_code, error="Non-JSON response", output=response.text)

        r = result.get("result", {})
        diag = r.get("diag", 0)
        success = diag == 200

        return ApiResult(
            success=success,
            diag=diag,
            error=r.get("error"),
            output=r.get("output"),
            data=r.get("data")
        )   

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, data: dict = None, **kwargs) -> httpx.Response:
        kwargs.setdefault("data", data)
        return self._request("POST", path, **kwargs)

    def put(self, path: str, data: dict = None, **kwargs) -> httpx.Response:
        kwargs.setdefault("data", data)
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> httpx.Response:
        return self._request("DELETE", path, **kwargs)

    def close(self):
        self._client.close()
