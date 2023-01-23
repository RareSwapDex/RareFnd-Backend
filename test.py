from pprint import pprint
import shopify
from decouple import config
from rich import print

with open("bulk.csv", "w") as file:
    file.write(
        "Handle	Title	Body (HTML)	Vendor	Product Category	Type	Tags	Published	Option1 Name	Option1 Value	Option2 Name	Option2 Value	Option3 Name	Option3 Value	Variant SKU	Variant Grams	Variant Inventory Tracker	Variant Inventory Qty	Variant Inventory Policy	Variant Fulfillment Service	Variant Price	Variant Compare At Price	Variant Requires Shipping	Variant Taxable	Variant Barcode	Image Src	Image Position	Image Alt Text	Gift Card	SEO Title	SEO Description	Google Shopping / Google Product Category	Google Shopping / Gender	Google Shopping / Age Group	Google Shopping / MPN	Google Shopping / AdWords Grouping	Google Shopping / AdWords Labels	Google Shopping / Condition	Google Shopping / Custom Product	Google Shopping / Custom Label 0	Google Shopping / Custom Label 1	Google Shopping / Custom Label 2	Google Shopping / Custom Label 3	Google Shopping / Custom Label 4	Variant Image	Variant Weight Unit	Variant Tax Code	Cost per item	Price / International	Compare At Price / International	Status"
    )
    for i in range(500000):
        print(f"RAREFND-CONTRIBUTION-{i+1}")
    exit()
SHOPIFY_TOKEN = config("SHOPIFY_TOKEN")
SHOPIFY_STORFRONT_TOKEN = config("SHOPIFY_STORFRONT_TOKEN")
SHOP_URL = config("SHOPIFY_SHOP_URL")
SHOPIFY_API = config("SHOPIFY_API_VERSION")
session = shopify.Session(SHOP_URL, SHOPIFY_API, SHOPIFY_TOKEN)

shopify.ShopifyResource.activate_session(session)

# response = shopify.Checkout.create(
#     {
#         "checkout": {
#             "email": "jelo@bld.ai",
#             "line_items": [{"variant_id": 44371994738988, "quantity": 1}],
#         }
#     }
# )
# print(response)
# products = shopify.Product.find(limit=10)
# for product in products:
#     pprint(str(product.to_dict()))
#     # Iterate through each variant
#     for variant in product.variants:
#         # Print the variant_id
#         print(variant.id)
exit()


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

# Shopify API endpoint
shopify_url = "https://rarefnd.myshopify.com/admin/api/2021-01/products.json"

# API access token
access_token = SHOPIFY_TOKEN

# Product data
data = {
    "product": {
        "title": "My new product",
        "published": True,
        "available": True,
        "variants": [{"price": "10.00", "sku": "my-new-product"}],
        "options": [{"name": "Size"}],
        # "metafields": [
        #     {
        #         "key": "custom_key",
        #         "value": "custom_value",
        #         "value_type": "string",
        #         "namespace": "global",
        #     }
        # ],
        # "images": [{"src": "https://example.com/my-new-product.jpg"}],
        "tags": "new, product",
        "channels": ["web", "mobile-app", "facebook", "pos"],
    }
}

# Make the API request
headers = {"X-Shopify-Access-Token": access_token}
response = requests.post(shopify_url, headers=headers, json=data)

# Check the response
if response.status_code == 201:
    response_json = response.json()
    product_id = response_json["product"]["id"]
    print("Product created successfully, product id :", product_id)
else:
    print(f"Error creating product: {response.status_code} - {response.text}")
