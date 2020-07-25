from ShopifyManagement import ManageOrder
import time
from multiprocessing import Process
from watchDog import setWatchDog

def shopifyOrderManagement():
    #Upon start
    while True:
        #Define which store to use
        store = 'DK'
        mo = ManageOrder(switch = store) #Instantiate the store
        
        #Check for existing orders for data base update - closed 
        status, orders = mo.getOrders(orderType = 'closed')
        if status is True:
            mo.insert_orders_to_database(orders)

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

        #Check for fulfillment
        mo.fulfill_and_capture()

        #Define which store to use
        store = 'HK'
        mohk = ManageOrder(switch = store) #Instantiate the storeß
        
        #Check for existing orders for data base update - closed

        status, orders = mohk.getOrders(orderType = 'closed')

        if status is True:
            mohk.insert_orders_to_database(orders)

        #Check for new orders for data base update - open
        status, orders = mohk.getOrders(orderType = 'open')

        if status is True:
            mohk.insert_orders_to_database(orders)

            #Check for sending warning SMS
            mohk.sms_delayWarn(orders)
        
            #Print out new orders
            mohk.print_orders()

            #Geoplotting
            mohk.geo_plotter()

        #Check for fulfillment
        mohk.fulfill_and_capture()

        #Stamp last system up time
        mohk.stampTime()

        print('system working...')
        time.sleep(5)

#Use multiprocessing to run main order tracking method and watch dog simultanously
if __name__ == '__main__':
    p1 = Process(target = shopifyOrderManagement, args = ())
    p2 = Process(target = setWatchDog, args = (1, 'lastTimeStamp.txt'))
    print('Starting the main process')
    p1.start()
    print('Main process started waiting now for 60 sec...')
    time.sleep(60)
    print('60 sec wait process passed starting watch dog')
    p2.start()
    print('watch dog started. System running again!')
    p1.join()
    p2.join()
