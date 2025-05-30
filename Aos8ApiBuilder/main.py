import pprint
from ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)

result = client.interface.show_interface_counters_errors("1/1/2")
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.output)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

