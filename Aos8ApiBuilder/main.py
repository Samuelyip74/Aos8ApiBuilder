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
result = client.vlan.delete_vlan(1003)
if result.success:
    print("✅ VLAN created successfully")
else:
    print(f"❌ VLAN creation failed (diag={result.diag}): {result.error}")

