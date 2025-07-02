### Aos8ApiBuilder

The Aos8ApiBuilder class provides an interface to construct, configure, and manage API endpoint groups for interacting with Alcatel-Lucent OmniSwitch devices using the AOS8 MIB-Based or CLI over HTTP. It acts as the main orchestrator for initializing the client and organizing the available API modules.

The builder is made up of two key classes and one data model:

+ ApiBuilder - A class to initialize the ApiBuilder with the OmniSwitch parameters (i.e. BaseURL, username, password etc).
+ ApiClient - A class that interact with OmniSwitch RestFUL API via GET, POST, PUT DELETE methods.
+ ApiResult - A data model for reading the results from OmniSwitch interaction.

The API endpoints extend ApiClient to interact with OmniSwitch for management functions, such as configuring VLAN, IP, OSPF etc.

You are welcome to develop and extend ApiClient to include custom API if not already available.