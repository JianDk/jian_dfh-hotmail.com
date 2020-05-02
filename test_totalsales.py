import shopify
import requests
API_KEY = "11d1233bd98782e8967a340918334686"
PASSWORD = "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"
API_VERSION = "2020-04"
shop_url = "https://%s:%s@alexanderystore.myshopify.com/admin/api/%s" % (API_KEY, PASSWORD, API_VERSION)

#Connect to the shop
shopify.ShopifyResource.set_site(shop_url)
order = shopify.Order.find(test = False, limit = 250, fulfillment_status = 'fulfilled')
print(len(order))

