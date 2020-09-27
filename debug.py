from ShopifyManagement import ManageOrder
import time

#Upon start
while True:

    #Define which store to use
    store = 'DK'
    mo = ManageOrder(switch = store) #Instantiate the store
    
    #Check for existing orders for data base update - closed 
    status, orders = mo.getOrders(orderType = 'closed')
    if status is True:
        mo.insert_orders_to_database(orders)
    else:
        continue

    #Check for new orders for data base update - open
    status, orders = mo.getOrders(orderType = 'open')

    if status is True:
        mo.insert_orders_to_database(orders)

        #Check for sending warning SMS
        mo.sms_delayWarn(orders)
    
        #Print out new orders
        mo.print_orders()

        #Geoplotting
        mo.geo_plotter()
    else:
        continue

    #Check for fulfillment
    mo.fulfill_and_capture()

    print('system working...')
    time.sleep(5)