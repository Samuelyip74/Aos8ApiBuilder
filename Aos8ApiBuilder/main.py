from ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://192.168.70.1")
    .setUsername("admin")
    .setPassword("switch123")
    .build()
)

# This will automatically re-authenticate on 401
# response = client.vlan.create_vlan(1000, "vlan-1000")
response = client.vlan.list()

print(response)
