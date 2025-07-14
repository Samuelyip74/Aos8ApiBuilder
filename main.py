import pprint
from aos8_api.ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)

result = client.interface.setInterfaceAdminStatus(ifindex="1023", admin_status=2)
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.output)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

