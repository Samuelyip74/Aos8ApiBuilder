import pprint
from ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)

result = client.interface.PortMappingConfig()
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.data)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

