import requests
from endpoints.vlan import VlanEndpoint


class AosApiClient:
    def __init__(self, username: str, password: str, base_url: str, verify_ssl: bool = False, debug: bool = False):
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({
            "User-Agent": "AOSApiClient/1.0",
            "Accept": "application/vnd.alcatellucentaos+json"
        })
        self._login()

        # Attach modular endpoint wrappers
        self.vlan = VlanEndpoint(self)

    def _login(self):
        url = f"{self.base_url}/auth/?&username={self.username}&password={self.password}"
        if self.debug:
            print(f"🔐 Logging in: {url}")
        response = self.session.get(url)
        if self.debug:
            print("🔐 Login response:", response.status_code, response.text)
        if response.status_code != 200:
            raise Exception("Login failed")
        if "wv_sess" not in [c.name for c in self.session.cookies]:
            raise Exception("Login succeeded but 'wv_sess' cookie not found")

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        if self.debug:
            print(f"🌐 Request: {method} {url}")
            if "params" in kwargs:
                print("Params:", kwargs["params"])
            if "data" in kwargs:
                print("Form Data:", kwargs["data"])
            if "json" in kwargs:
                print("JSON:", kwargs["json"])

        response = self.session.request(method, url, **kwargs)

        if response.status_code == 401:
            print("🔁 401 Unauthorized, retrying after login...")
            self._login()
            response = self.session.request(method, url, **kwargs)

        if self.debug:
            print("⬅️ Response:", response.status_code)
            print(response.text)

        response.raise_for_status()
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, data: dict = None, **kwargs) -> requests.Response:
        kwargs.setdefault("data", data)
        return self._request("POST", path, **kwargs)

    def put(self, path: str, data: dict = None, **kwargs) -> requests.Response:
        kwargs.setdefault("data", data)
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self._request("DELETE", path, **kwargs)

    def close(self):
        self.session.close()
