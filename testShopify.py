import shopify
import requests
import database_manager as dbman
import os
import datetime

switch = 'HK'
API_VERSION = "2020-04"

if switch == 'DK':
    API_KEY = "f7bf71f3f3b7ce0a6f75863bdfccf53e"
    PASSWORD = "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"
    shop_url = "https://%s:%s@jian-xiong-wu.myshopify.com/admin/api/%s" % (API_KEY, PASSWORD, API_VERSION)
    databasePath = 'orderDBDK.db'

if switch == 'HK':
    API_KEY = "11d1233bd98782e8967a340918334686"
    PASSWORD = "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"
    shop_url = "https://%s:%s@alexanderystore.myshopify.com/admin/api/%s" % (API_KEY, PASSWORD, API_VERSION)
    databasePath = 'orderDBHK.db'

#Connect to the shop
shopify.ShopifyResource.set_site(shop_url)

#Check if database exists
if os.path.exists(databasePath) is False:
    dbman.createDB(databasePath)

#Check if table name exists. If not, it will be created
tablename = ['customer', 'items', 'order_execution']
dbman.chkTableExists(databasePath, tablename)

#Check for new incoming orders within the past 60 days
orders = shopify.Order.find(fulfillment_status = False, test = False) #test should be set to False in production
#For each orders, check if order is already in database. If not, insert it
for item in orders:
    print(item.name) #The number
    print(item.customer.first_name, item.customer.last_name)
    print(item.shipping_address.address1)
    print(item.shipping_address.address2)
    print(item.shipping_address.zip)
    print(item.shipping_address.city)
    print(item.shipping_address.country)
    print(item.shipping_address.latitude)
    print(item.shipping_address.longitude)
    print(item.customer.phone)
    print(item.customer.email)
    print('here is additional details')
    for i in item.note_attributes:
        print(i.value)
    
#Get a list of all payouts
payout_url = shop_url  + "/shopify_payments/payouts.json"
resp = requests.get(payout_url)
resp = resp.json()
currentMonthPayout = list()

for item in resp['payouts']:
    print(item)
    print('\n')

#Current month
current_month = datetime.datetime.now().month
date = '2020-04-06'
date = datetime.datetime.strptime(date, "%Y-%m-%d")
if current_month == date.month:
    print('yes')
print(date.month)