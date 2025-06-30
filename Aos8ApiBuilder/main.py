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
    name="vlan-999",
    address="11.1.1.99",
    mask="255.255.255.0",
    device="Vlan",
    vlan_id=99,
    local_proxy_arp=True
    )
if result.success:
    print("✅ Operation successfully")
    #pprint.pprint(result.data)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

