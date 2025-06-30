import pprint
from ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)

result = client.ip.create_IP_Interface(
    name="int-999",
    address = "1.1.1.99",
    mask = "255.255.255.0",
    vlan_id = 99,
)
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.data)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

