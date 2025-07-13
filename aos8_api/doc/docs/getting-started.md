### Getting Started

#### Install Aos8ApiBuilder

Before you can use Aos8ApiBuilder, you’ll need to install it via pip. 

To install the library, type "pip install aos8-api"

#### Write your first API call

Installed Aos8ApiBuilder already? Good. Now try the below tutorial, which walks you through creating a basic API call. 

```
import pprint
from aos8_api.ApiBuilder import AosApiClientBuilder

client = (
    AosApiClientBuilder()
    .setBaseUrl("https://<ip-address-of-omniswitch>")
    .setUsername("<username>")
    .setPassword("<password>")
    .build()
)

result = client.interface.admin_enable("1/1/28-30")
if result.success:
    print("✅ Operation successfully")
    pprint.pprint(result.output)
else:
    print(f"❌ Operation failed (diag={result.diag}): {result.error}")

 
``` 

    
