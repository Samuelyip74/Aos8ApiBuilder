import pprint
from aos8_api.ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)

result = client.cli.sendCommand("show configuration snapshot")
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.output)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

