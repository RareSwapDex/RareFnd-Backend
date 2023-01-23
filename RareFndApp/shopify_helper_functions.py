from pprint import pprint
import json
import requests
from decouple import config


SHOPIFY_TOKEN = config("SHOPIFY_TOKEN")
SHOP_URL = config("SHOPIFY_SHOP_URL")
SHOPIFY_API = config("SHOPIFY_API_VERSION")
SHOPIFY_STORFRONT_TOKEN = config("SHOPIFY_STORFRONT_TOKEN")
api_endpoint = "/admin/api/2021-01/products.json"


def shopify_create_product(
    name, price, contributor_email, project_contract_address, project_id
):
    product_data = {
        "product": {
            "title": name,
            "body_html": "",
            "vendor": "rarefnd",
            "published": True,
            "available": True,
            "published_scope": "global",
            "published_at": "2022-01-03T04:07:00Z",
            "variants": [
                {
                    "price": price,
                    "sku": f"",
                    "inventory_management": "shopify",
                    "inventory_quantity": 1,
                    "weight": 0,
                    "weight_unit": "kg",
                    "requires_shipping": False,
                }
            ],
            "product_type": "Digital",
            "tags": ["Barnes \u0026 Noble", "Big Air", "John's Fav"],
            "metafields": [
                {
                    "name": name,
                    "contributor_email": contributor_email,
                    "project_contract_address": project_contract_address,
                    "project_id": project_id,
                }
            ],
        }
    }
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"https://{SHOP_URL}{api_endpoint}",
        headers=headers,
        data=json.dumps(product_data),
    )
    pprint(response)
    if response.status_code != 201:
        return {"success": False}
    response_json = response.json()
    variant_id = response_json["product"]["variants"][0]["id"]
    return {"success": True, "variant_id": variant_id}


def create_checkout(variant_id, contributor_email, success_url, fail_url):
    # query = """
    #     mutation {
    #     checkoutCreate(input: {
    #       lineItems: [{ variantId: "gid:\/\/shopify\/ProductVariant\/%s", quantity: 1 }], email: "%s"

    #     }) {
    #       checkout {
    #         id
    #         webUrl
    #         lineItems(first: 5) {
    #           edges {
    #             node {
    #               title
    #               quantity
    #             }
    #           }
    #         }
    #       }
    #     }
    #   }
    # """ % (
    #     variant_id,
    #     contributor_email,
    # )

    query = """
        mutation {
        checkoutCreate(input: {
          lineItems: [{ variantId: "gid:\/\/shopify\/ProductVariant\/44369908760876", quantity: 1 }], email: "customer@example.com"

        }) {
          checkout {
            id
            webUrl
            lineItems(first: 5) {
              edges {
                node {
                  title
                  quantity
                }
              }
            }
          }
        }
      }
    """

    headers = {
        "X-Shopify-Storefront-Access-Token": SHOPIFY_STORFRONT_TOKEN,
    }

    response = requests.post(
        "https://rarefnd.myshopify.com/api/2021-10/graphql.json",
        headers=headers,
        json={"query": query},
    )

    if response.status_code != 200:
        return {"success": False}

    response_json = response.json()
    pprint(response_json)
    try:
        web_url = response_json["data"]["checkoutCreate"]["checkout"]["webUrl"]
    except Exception:
        return {"success": False}
    return {"success": True, "web_url": web_url}
