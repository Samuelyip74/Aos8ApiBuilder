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
result = client.vpa.add_port_to_vlan(vlan_id=999,port_id="1/1/10")
if result.success:
    print("✅ Vlan operation successfully")
    print(result.output)
else:
    print(f"❌ VLAN creation failed (diag={result.diag}): {result.error}")

result = client.vpa.remove_port_from_vlan(vlan_id=999,port_id="1/1/10")
if result.success:
    print("✅ Vlan operation successfully")
    print(result.output)
else:
    print(f"❌ VLAN creation failed (diag={result.diag}): {result.error}")    

