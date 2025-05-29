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
result = client.ip.delete(if_name="intvlan1")
if result.success:
    print("✅ Operation successfully")
    print(result.output)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 

