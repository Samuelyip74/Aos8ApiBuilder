import pprint
from aos8_api.ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)
result = client.interface.setInterfaceAlias(ifindex="1001", alias=" ")
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.output)
    client.close()
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

