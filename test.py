from pprint import pprint

# import shopify
from decouple import config
from datetime import datetime

SHOPIFY_TOKEN = config("SHOPIFY_TOKEN")
# SHOP_URL = config("SHOPIFY_SHOP_URL")
# SHOPIFY_API = config("SHOPIFY_API_VERSION")
# session = shopify.Session(SHOP_URL, SHOPIFY_API, SHOPIFY_TOKEN)
# shopify.ShopifyResource.activate_session(session)

# # products = shopify.Product.find(limit=10)
# # for product in products:
# #     pprint(str(product.to_dict()))
# #     # Iterate through each variant
# #     # for variant in product.variants:
# #     #     # Print the variant_id
# #     #     print(variant.id)


# def shopify_create_product(
#     name, price, contributor_email, project_contract_address, project_id
# ):
#     product = shopify.Product()
#     product.title = name
#     product.price = price
#     product.metafields = [
#         {
#             "name": name,
#             "contributor_email": contributor_email,
#             "project_contract_address": project_contract_address,
#             "project_id": project_id,
#         }
#     ]
#     inventory_quantity = 1
#     product.save()


# shopify_create_product(
#     "test 34", 22, "contributor_email@gmail.com", "project_contract_address", 1
# )
# exit()

# import json
# import requests

# # Prepare the data for the checkout
# query = """
#     mutation {
#     checkoutCreate(input: {
#       lineItems: [{ variantId: "gid:\/\/shopify\/ProductVariant\/44369884217644", quantity: 1 }], email: "customer@example.com"

#     }) {
#       checkout {
#         id
#         webUrl
#       }
#     }
#   }
# """

# # Prepare the headers for the request
# headers = {
#     # "Content-Type": "application/json",
#     "X-Shopify-Storefront-Access-Token": "6c02f76f0e787aa37f215bef8da6085d",
# }

# # Send the request to create the checkout
# response = requests.post(
#     "https://rarefnd.myshopify.com/api/2021-10/graphql.json",
#     headers=headers,
#     json={"query": query},
# )

# # Print the response
# print(json.dumps(response.json(), indent=4))


import json
import requests

# Define your Shopify store URL and access token
store_url = "https://rarefnd.myshopify.com"
access_token = SHOPIFY_TOKEN

################################################################

headers = {"X-Shopify-Access-Token": access_token}

response = requests.get(
    store_url + "/admin/api/2021-01/custom_collections.json", headers=headers
)

# Parse the response
collections = response.json()["custom_collections"]

# Print the collection names
for collection in collections:
    print(collection)
exit()

################################


# GraphQL query to create a product
query_create = """
mutation {
  productCreate(input: {
    title: "My new product 77",
    variants: [
      {
        price: "10.00",
        sku: "new-product-sku",
      }
    ],
  }) {
    product {
      id
    }
  }
}
"""

# Headers for the request
headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": access_token}

# Make the request
response = requests.post(
    f"{store_url}/admin/api/2020-04/graphql.json",
    json={"query": query_create},
    headers=headers,
)

# Parse the response
response_json = json.loads(response.text)
pprint(response_json)
# Extract the product ID
product_id = response_json["data"]["productCreate"]["product"]["id"]
# GraphQL query to make the product available in all sales channels
# Channel ID, publication ID, and publish date
channel_id = "gid://shopify/Channel/12345"
publication_id = "gid://shopify/Publication/67890"
publish_date = "2022-10-01T00:00:00Z"

# GraphQL query to make the product available in all sales channels
query_publish = f"""
mutation {{
  publishablePublish(id: "{product_id}", input: {{
    channelId: "{channel_id}",
    publicationId: "{publication_id}",
    publishDate: "{publish_date}"
  }}) {{
    publishable {{
      availablePublicationCount
    }}
  }}
}}
"""

# Make the request
response = requests.post(
    f"{store_url}/admin/api/2020-04/graphql.json",
    json={"query": query_publish},
    headers=headers,
)

# Parse the response
response_json = json.loads(response.text)
print(response_json)
# Print the publishable ID
print(response_json["data"]["publishablePublish"]["publishable"]["id"])
