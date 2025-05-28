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
result = client.vlan.edit_vlan(1003, mtu=1280)
if result.success:
    print("✅ Vlan operation successfully")
    print(result.error)
else:
    print(f"❌ VLAN creation failed (diag={result.diag}): {result.error}")

