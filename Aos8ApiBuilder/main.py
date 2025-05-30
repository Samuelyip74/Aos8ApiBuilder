import pprint
from ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)

# This will automatically re-authenticate on 401
# response = client.vlan.create_vlan(1001, "vlan-1001")
# response = client.vlan.list()
result = client.interface.admin_enable("1/1/28-30")
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.output)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

