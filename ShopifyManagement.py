import datetime
import logging
import requests
from calendar import monthrange
import os
import database_manager as dbman
from ShopifyPrinter_win10 import Printer
import json
import time
import GeoPlotter
from twilio.rest import Client

class ManageOrder:
    def __init__(self, **kwargs):
        self.API_VERSION = "2020-04"

        if kwargs['switch'] == 'DK':
            self.API_KEY = "f7bf71f3f3b7ce0a6f75863bdfccf53e"
            self.PASSWORD = "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"
            self.shop_url = "https://%s:%s@jian-xiong-wu.myshopify.com/admin/api/%s" % (self.API_KEY, self.PASSWORD, self.API_VERSION)
            self.databasePath = 'orderDBDK.db'
            self.store = 'DK'

        if kwargs['switch'] == 'HK':
            self.API_KEY = "11d1233bd98782e8967a340918334686"
            self.PASSWORD = "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"
            self.shop_url = "https://%s:%s@alexanderystore.myshopify.com/admin/api/%s" % (self.API_KEY, self.PASSWORD, self.API_VERSION)
            self.databasePath = 'orderDBHK.db'
            self.store = 'HK'
        
        #DEfine conversion rate from HKD to DKK
        self.conversion_HKD_DKK = 0.89

        #Define printer parameter
        self.printerParam = dict()
        self.printerParam['printerNear'] = {'connectionMethod' : 'usb',
        'printerDriverName' : "EPSON TM-T20II Receipt"
        }
        self.printerParam['printerFar'] = {}
        self.printerParam['printerFar'] = {
            'connectionMethod' : 'network',
            'host' : '192.168.1.50',
            'port' : 9100
        }

        #Load in the translator file for print
        with open('Shopify_item2print.txt', 'r') as f:
            self.print_translation = json.load(f)
        
        #Load sms credientials
        
        with open('twilio_crediential.txt') as f:
            self.sms_cred = json.load(f)
      
        #Assure that the sqlite3 data base exists 
        if os.path.exists(self.databasePath) is False:
            dbman.createDB(self.databasePath)
    
    def incomeStatus(self, switch):
        '''
        get how much income is currently in HK and DK site for the current month. The currency is in DK.
        '''
        #Get current income in HK for this month
        self.__init__(switch = switch)
        currentMonth = datetime.datetime.now().month
        
        #Get the payouts from HK for this month
        payout_url = self.shop_url  + "/shopify_payments/payouts.json"
        resp = requests.get(url = payout_url)
        if resp.status_code != 200:
            status = False
            amount = False
            self.logging('debug', 'Failed to request for payouts from ' + switch)
            #Need to create a log file here
            return status, amount

        resp = resp.json()['payouts']
        month_income = list()
        for item in resp:
            #Check if payout date is within current date
            date = datetime.datetime.strptime(item['date'], "%Y-%m-%d")
            if date.month == currentMonth and item['status'] != 'failed':
                #The income for this transaction will be counted
                
                #Get currency format
                if item['currency'] == 'HKD':
                    month_income.append(float(item['amount']) * self.conversion_HKD_DKK)
                elif item['currency'] == 'DKK':
                    month_income.append(float(item['amount']))

        amount = round(sum(month_income))

        #Get the balance in the account that is not yet included in payouts
        balance_url = self.shop_url + "/shopify_payments/balance.json"
        resp = requests.get(url = balance_url)
        if resp.status_code != 200:
            self.logging('debug', 'Failed to retrieve the balance from ' + switch)
            status = False
            amount = False
            return status, amount
        balance = resp.json()['balance'][0]
        if balance['currency'] == 'HKD':
            balance = float(balance['amount']) * self.conversion_HKD_DKK
        elif balance['currency'] == 'DKK':
            balance = float(balance['amount'])

        amount = amount + round(balance) 
        status = True
        return status, amount
    
    def account_switch_decision(self, maxIncome):
        '''
        Check if amount in DK account and decide if account should be changed
        '''
        status, amount = self.incomeStatus(switch = 'DK')
        if status == False:
            status = False
            self.logging('debug', 'Cannot get income status from DK site')
            account_switch = False
            return status, account_switch
        
        #Based on the amount from current month decision is being made
        if amount < maxIncome:
            #Calculate how many days there is in month
            total_days = monthrange(datetime.datetime.now().year, datetime.datetime.now().month)
            total_days = total_days[1]
            current_day = datetime.datetime.now().day
            daysleft = total_days - current_day +1
            #Target earnings per day
            print(total_days)
            targetIncome_per_day = round(maxIncome / total_days)
            print(targetIncome_per_day)
            #How much is left to be earned
            left_income = maxIncome - amount
            left_income_per_day = left_income / daysleft
            print(left_income_per_day)
            if left_income_per_day < targetIncome_per_day:
                account_switch = 'HK'
                status = True
                return status, account_switch
            else:
                account_switch = 'DK'
                status = True
                return status, account_switch

    def capture_transaction(self, order_id):
        #Retrieves a list of transactions associated with the order
        url_transaction = self.shop_url + f"/orders/{order_id}/transactions.json"
        resp = requests.get(url = url_transaction)
        if resp.status_code != 200:
            self.logging('debug','Failed to retrieve order id ' + str(order_id) + ' for capture payment (url_transaction)')
            status = False
            return status

        #Get currency and amount
        currency = resp.json()['transactions'][0]['currency']
        amount = resp.json()['transactions'][0]['amount']
        #Post for capture
        postbody = dict()
        postbody['transaction'] = dict()
        postbody['transaction']['currency'] = currency
        postbody['transaction']['amount'] = amount
        postbody['transaction']['kind'] = "capture"
        url_capture_payment = self.shop_url + f"/orders/{order_id}/transactions.json"
        resp = requests.post(url = url_capture_payment, json = postbody)
        if resp.status_code != 201 and resp.status_code != 422:
            self.logging('debug', 'post payment capture status code ' + str(resp.status_code))
            status = False
            return status

        status = True
        return status

    def convert_pickup_datetime(self, datestr, timestr):
        '''
        convert shopify pickup date and time to datetime format
        '''
        datestr = datestr + '-' + timestr
        timeformat = '%d/%m/%Y-%H:%M'
        date_and_time = datetime.datetime.strptime(datestr, timeformat)
        return date_and_time
    
    def convert_delivery_datetime(self, datestr, timestr, option):
        '''
        convert shopify delivery date and time to datetime format
        datestr is given as e.g. 23/04/2020 
        timestr is given as e.g. 6:30 PM - 7:30 PM
        option can either be start_time or end_time provided as string. If start time, the datetime will be formed by using 
        6:30 PM as start time as in this example. If end_time datetime will be formed using 7:30 PM as in this example.
        '''
        #Split the time to start time and end time
        timestr = timestr.split('-')
        start_time = timestr[0].strip()
        end_time = timestr[1].strip()
        
        timeformat = '%d/%m/%Y-%I:%M %p'
        if option == 'start_time':
            timestr = datestr + '-' + start_time
            date_and_time = datetime.datetime.strptime(timestr, timeformat)
        
        if option == 'end_time':
            timestr = datestr + '-' + end_time
            date_and_time = datetime.datetime.strptime(timestr, timeformat)

        return date_and_time         

    def created_at_to_datetime(self, created_at):
        '''
        converts created_at to datetime object without daylight saving awareness. Input created_at 
        as string in format "%Y-%m-%dT%H:%M:%S%z"
        '''
        
        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z")
        created_at = created_at.replace(tzinfo=None)
        return created_at
   
        
    def fulfill_and_capture(self, **kwargs):
        #Get order_id from unfulfilled orders
        data = dbman.get_incomplete_orders(self.databasePath)
        if not data:
            return
        
        #Loop over the unfulfilled orders and decide if it should be fulfilled
        for item in data:
            if item[-1].strip() == 'now':
                #Order should be closed and payment captured
                status_fulfill = self.fulfill_order(item[1])
                status_payment_capture = self.capture_transaction(item[1])
                if status_fulfill is False or status_payment_capture is False:
                    continue
                else: #update the data base with FULFILL_PAYMENT_CAPTURE to yes
                    dbman.set_fulfill_payment_capture_to_yes(self.databasePath, item[0])
            
            if item[-1].strip() == 'no':
                #Get current time
                now = datetime.datetime.now()
                #Check delivery type and convert the time 
                if item[2] == 'pickup':
                    date_and_time = self.convert_pickup_datetime(item[3], item[4])
                    if now > date_and_time + datetime.timedelta(minutes=60):
                        #After one hour from execution time, pickup will be closed
                        status_fulfill = self.fulfill_order(item[1])
                        status_payment_capture = self.capture_transaction(item[1])
                        if status_fulfill is False or status_payment_capture is False:
                            self.logging('debug', 'Problem with fulfill or capture payment for item ' + str(item[0]))
                        else:
                            dbman.set_fulfill_payment_capture_to_yes(self.databasePath, item[0])
                
                if item[2] == 'delivery':
                    date_and_time = self.convert_delivery_datetime(item[3], item[4], 'end_time')
                    if now > date_and_time + datetime.timedelta(minutes=60):
                        #After one hour from end_time the order will be closed
                        status_fulfill = self.fulfill_order(item[1])
                        status_payment_capture = self.capture_transaction(item[1])
                        if status_fulfill is False or status_payment_capture is False:
                            self.logging('debug', 'Problem with fulfill or capture payment for item ' + str(item[0]))
                        else:
                            dbman.set_fulfill_payment_capture_to_yes(self.databasePath, item[0])

    def fulfill_order(self, order_id):
        '''
        Given the order id a request is made to Shopify to fulfill the order
        '''
        #Start by retrieving the specific order
        order_url = self.shop_url + f"/orders/{order_id}.json"
        resp = requests.get(order_url)
        if resp.status_code != 200:
            self.logging('debug', 'Failed to retrieve order from fulfill_and_capture')
            status = False
            return status
        
        #Obtain the line_items where the variant_id is stored
        line_items = resp.json()['order']['line_items']

        #Obtain inventory_item_id for each variant id
        line_items_id = list()
        for i in line_items:
            line_items_id.append({'id' : str(i['id'])})
            url_inventory_item_id = self.shop_url + f"/variants/{i['variant_id']}.json"
            resp_inventory_ítem_id = requests.get(url = url_inventory_item_id)  

            if resp_inventory_ítem_id.status_code != 200:
                status = False
                self.logging('debug', 'Failed to retrieve inventory item id for variant id ' + str(i['variant_id']))
                return status
            
            inventory_item_id = resp_inventory_ítem_id.json()['variant']['inventory_item_id']
            
            #Get the location id
            url_location_id = self.shop_url + f"/inventory_levels.json?inventory_item_ids={inventory_item_id}"
            resp_location_id = requests.get(url = url_location_id)

            if resp_location_id.status_code != 200:
                status = False
                self.logging('debug', 'Failed to retrieve location id for inventory item id ' + str(inventory_item_id))
                return status
            
            location_id = resp_location_id.json()['inventory_levels'][0]['location_id']

        #Build the post payload for order fulfillment
        postbody = dict()
        postbody['fulfillment'] = dict()
        postbody['fulfillment']['location_id'] = location_id
        postbody['fulfillment']['tracking_number'] = ''
        postbody['fulfillment']['line_items'] = list()
        postbody['fulfillment']['line_items'] = line_items_id

        #post fulfillment
        url_fulfillment = self.shop_url + f"/orders/{order_id}/fulfillments.json"
        resp_post_fulfillment = requests.post(url = url_fulfillment, json = postbody)
        if resp_post_fulfillment.status_code != 200 and resp_post_fulfillment.status_code != 201 and resp_post_fulfillment.status_code != 422:
            self.logging('debug', 'post fulfillment failed status code ' + str(resp_post_fulfillment.status_code))
            status = False
            return status
        
        status = True
        return status

    def geo_plotter(self):
        GeoPlotter.GeoPlotter(home_latitude = 55.677063, 
        home_longitude = 12.573435, 
        radius = 11000, 
        dbpath = self.databasePath, 
        storename = self.store)

    def getOrders(self, **kwargs):
        '''
        Query Shopify for orders. Returns a list of orders. **kwargs: orderType = 'open' query Shopify for new orders not yet 
        fulfilled. orderType = 'closed' query Shopify for closed orders.
        '''
        order_url = self.shop_url + "/orders.json"
        if kwargs['orderType'] == 'open':
            created_at = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
            pay_load = {'test' : False,
            'created_at_max' : created_at,
            'status' : 'open',
            'limit' : 250} #Will not implement the look for next page, as usually there will never be more than 50 new orders a day

            resp = requests.get(url = order_url, params = pay_load)

            if resp.status_code != 200:
                self.logging('debug', 'Failed to request for open orders from getOrders')
                status = False
                orders = False
                return status, orders
            
            orders = resp.json()['orders']
            status = True
            return status, orders
        
        if kwargs['orderType'] == 'closed':
            pay_load = {'test' : False,
            'limit' : 250,
            'status' : 'closed'}
            
            resp = requests.get(url = order_url, params = pay_load)
            if resp.status_code != 200:
                self.logging('debug', 'Failed to request closed orders')
                status = False
                orders = False
                return status, orders
            orders = resp.json()['orders']
            #Check for additional pages, if exists keep querying
            in_loop = True
            while in_loop:
                #If next page exists, retrieve it
                if 'link' in resp.headers and 'rel="next' in resp.headers['link']:
                    #Obtain the new link for next page
                    link = resp.headers['Link'].split('page_info=')
                    link = link[1].split('>;')[0]
                    next_page_order_url = order_url + '?page_info=' + link + '&limit=250'
                    resp = requests.get(url = next_page_order_url)
                    
                    if resp.status_code != 200:
                        self.logging('debug', 'failed to retrieve closed orders in next page')
                        status = False
                        orders = False
                        return status, orders
                    
                    #Append the new orders into the existing ones from previous pages
                    for item in resp.json()['orders']:
                        orders.append(item)
                
                else:
                    in_loop = False
                    status = True 
                    return status, orders
    
    def insert_orders_to_database(self, orders):
        #Send to database_manager for order insertion
        dbman.insert_orders_to_database(self.databasePath, orders)
    
    def print_orders(self):
        #Query orders from the data base
        printable_orderno = dbman.get_printable_orderno(self.databasePath)

        for item in printable_orderno: #These items are printable order, but still there is a need to check if we are within time frame for print            
            now = datetime.datetime.now()

            #Get customer information
            customer_info = dbman.get_customer(self.databasePath, item[0])
            #Get items that was ordered by customer
            order_items = dbman.get_orderItems(self.databasePath, item[0])

            if item[8] == 'now':
                if item[3] == 'delivery':
                    #Send print to packer
                    #Instantiate the printer first
                    printer = Printer(self.printerParam['printerNear'])
                    printer.printOrder_packer(item, customer_info, order_items, self.print_translation)

                    printer = Printer(self.printerParam['printerNear'])
                    printer.printDriver(customer_info, item)
                    
                    printer = Printer(self.printerParam['printerFar'])
                    printer.printOrder_kitchen(item, customer_info, order_items, self.print_translation)

                    #set print status to yes in the data base
                    dbman.setPrintedStatus(self.databasePath, item[0], 'yes')

                if item[3] == 'pickup':
                    printer = Printer(self.printerParam['printerNear'])
                    printer.printOrder_packer(item, customer_info, order_items, self.print_translation)
                    
                    printer = Printer(self.printerParam['printerFar'])
                    printer.printOrder_kitchen(item, customer_info, order_items, self.print_translation)
                    #set print status to yes in the data base
                    dbman.setPrintedStatus(self.databasePath, item[0], 'yes')        

            if item[3] == 'delivery':
                execution_time = self.convert_delivery_datetime(item[4], item[5], 'start_time') 
                execution_time = execution_time - datetime.timedelta(minutes=60)
                if now >= execution_time:
                    #Send print to packer
                    #Instantiate the printer first
                    printer = Printer(self.printerParam['printerNear'])
                    printer.printOrder_packer(item, customer_info, order_items, self.print_translation)

                    printer = Printer(self.printerParam['printerNear'])
                    printer.printDriver(customer_info, item)
                    
                    printer = Printer(self.printerParam['printerFar'])
                    printer.printOrder_kitchen(item, customer_info, order_items, self.print_translation)

                    #set print status to yes in the data base
                    dbman.setPrintedStatus(self.databasePath, item[0], 'yes')

            if item[3] == 'pickup':
                execution_time = self.convert_pickup_datetime(item[4], item[5]) 
                execution_time = execution_time - datetime.timedelta(minutes=60)

                if now >= execution_time:
                    printer = Printer(self.printerParam['printerNear'])
                    printer.printOrder_packer(item, customer_info, order_items, self.print_translation)
                    
                    printer = Printer(self.printerParam['printerFar'])
                    printer.printOrder_kitchen(item, customer_info, order_items, self.print_translation)
                    #set print status to yes in the data base
                    dbman.setPrintedStatus(self.databasePath, item[0], 'yes')
    
    def sms_delayWarn(self, orders):
        #Get the new incoming orders 
        for item in orders:
            #Start by extracting orderno
            orderno = item['name'].split('#')[1]
            #Query the data base to obtain customer name, created_at, and delivery wished
            
            #Connect to data base and extract customer info
            customer = dbman.get_customer(self.databasePath, orderno)

            #Get customer order execution data
            order_execution = dbman.get_order_execution(self.databasePath, orderno)
            mobile_phone = customer[3]
            
            if order_execution[3] == 'delivery' and order_execution[7] == 'no': #no delay warning sent yet
                #Delay date:

                #Convert to datetime
                created_at = self.created_at_to_datetime(order_execution[6])
                start_delivery_time = self.convert_delivery_datetime(order_execution[4], order_execution[5], 'start_time')
                end_delivery_time = self.convert_delivery_datetime(order_execution[4], order_execution[5], 'end_time')
                
                #set the expected time with delay taken into account
                expected_delivery = end_delivery_time + datetime.timedelta(minutes = 30)
                expected_delivery = expected_delivery.strftime('%H:%M')

                #Evaluate how long in advance the order was created
                created_in_advance = (start_delivery_time - created_at).total_seconds() /60 #minutes customer created the order in advance
                
                if created_in_advance <= 0: #Greedy delivery time, where created at time is in the delivery time frame
                    #no hesistation. Send delay sms
                    expected_delivery = end_delivery_time + datetime.timedelta(minutes = 30)
                    expected_delivery.strftime('%Y-%m-%d %H:%M%S')
                    
                    smstext = f'''Dear {customer[1]},
                    
Thanks for your order. We are currently very busy, and expect to deliver your order to you at around {expected_delivery}. Thanks for your understanding.

This sms cannot be answered. For direct contact you can reach us at 33 12 88 28
            
                    
Hidden Dimsum with Thanks!'''

                    #send first dummy sms to myself to assure the sanity of the sms
                    self.send_sms(smstext, '+4542788282') #change to mobile_phone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    self.send_sms(smstext, mobile_phone)
                    dbman.delay_warn(self.databasePath, orderno, 'yes')
        
                if created_in_advance > 0 and created_in_advance < 30:
                    #Check how many other orders we have in the requested delivery time
                    tmp_timedelta = (end_delivery_time - start_delivery_time) / 2
                    midpoint = start_delivery_time + tmp_timedelta

                    delay_date = order_execution[4]
                    deliver_data, pickup_data = dbman.count_orders(self.databasePath, delay_date)

                    #From the received order, count order amount in the same delivery time frame
                    counter = 0
                    for item in deliver_data:
                        #For each delivery data, check if our midpoint is within the time-span
                        existing_order_delivery_start = self.convert_delivery_datetime(item[4], item[5], 'start_time')    
                        existing_order_delivery_end = self.convert_delivery_datetime(item[4], item[5], 'end_time')
                        if midpoint >= existing_order_delivery_start and midpoint <= existing_order_delivery_end:
                            counter += 1
                    
                    for item in pickup_data:
                        #For each pickup data, check if our midpoint is within the time-span
                        existing_order_pickup_time = self.convert_pickup_datetime(item[4], item[5])
                        #If midpoint is larger than 30 min earlier than existing pickup time and smaller than existing pickup time
                        #counter is increased by 1
                        if midpoint >= existing_order_pickup_time - datetime.timedelta(minutes=30) and midpoint <= existing_order_pickup_time:
                            counter += 1

                    if counter > 4:
                        expected_delivery = end_delivery_time + datetime.timedelta(minutes = 30)
                        expected_delivery.strftime('%Y-%m-%d %H:%M%S')

                        smstext = f'''Dear {customer[1]},
                    
Thanks for your order. We are currently very busy, and expect to deliver your order to you at around {expected_delivery}. Thanks for your understanding.

This sms cannot be answered. For direct contact you can reach us at 33 12 88 28
            
                    
Hidden Dimsum with Thanks!'''

                        self.send_sms(smstext, mobile_phone)
                        self.send_sms(smstext, '+4542788282') #Change to mobile_phone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        dbman.delay_warn(self.databasePath, orderno, 'yes')
            
            if order_execution[3] == 'pickup' and order_execution[7] == 'no': #no delay warning sent yet
                #Delay date:

                #Convert to datetime
                created_at = self.created_at_to_datetime(order_execution[6])
                pickup_time = self.convert_pickup_datetime(order_execution[4], order_execution[5])
                
                #set the expected time with delay taken into account
                expected_pickup_time = pickup_time + datetime.timedelta(minutes = 30)
                expected_pickup_time = expected_pickup_time.strftime('%H:%M')

                #Evaluate how long in advance the order was created
                created_in_advance = (pickup_time - created_at).total_seconds() /60 #minutes customer created the order in advance
                
                if created_in_advance <= 0: #Greedy pickup time, where created pickup time is after pickup. This logic should not be possible due to restrictions in the webpage
                    #no hesistation. Send delay sms
                    
                    smstext = f'''Dear {customer[1]},
                    
Thanks for your order. We are currently very busy, and as a consequence there can be a delay in your pickup. Your pickup will be ready at {expected_pickup_time}. We will notify you, should it be ready for pickup earlier. Thanks for your understanding.

This sms cannot be answered. For direct contact you can reach us at 33 12 88 28
            
                    
Hidden Dimsum with Thanks!'''

                    #send first dummy sms to myself to assure the sanity of the sms
                    self.send_sms(smstext, '+4542788282') #change to mobile_phone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    self.send_sms(smstext, mobile_phone)
                    dbman.delay_warn(self.databasePath, orderno, 'yes')
        
                if created_in_advance > 0 and created_in_advance < 30:
                    #Check how many other orders we have in the requested time range

                    delay_date = order_execution[4]
                    deliver_data, pickup_data = dbman.count_orders(self.databasePath, delay_date)

                    #From the received order, count order amount in the same delivery time frame
                    counter = 0
                    for item in deliver_data:
                        #For each delivery data, check if our midpoint is within the time-span
                        existing_order_delivery_start = self.convert_delivery_datetime(item[4], item[5], 'start_time')    
                        existing_order_delivery_end = self.convert_delivery_datetime(item[4], item[5], 'end_time')
                        if pickup_time >= existing_order_delivery_start and pickup_time <= existing_order_delivery_end:
                            counter += 1
                    
                    for item in pickup_data:
                        #For each pickup data, check if our midpoint is within the time-span
                        existing_order_pickup_time = self.convert_pickup_datetime(item[4], item[5])
                        #If midpoint is larger than 30 min earlier than existing pickup time and smaller than existing pickup time
                        #counter is increased by 1
                        if pickup_time >= existing_order_pickup_time - datetime.timedelta(minutes=30) and pickup_time <= existing_order_pickup_time:
                            counter += 1

                    if counter > 4:

                        smstext = f'''Dear {customer[1]},
                    
Thanks for your order. We are currently very busy, and as a consequence there can be a delay in your pickup. Your pickup will be ready at {expected_pickup_time}. We will notify you, should it be ready for pickup earlier. Thanks for your understanding.

This sms cannot be answered. For direct contact you can reach us at 33 12 88 28
            
                    
Hidden Dimsum with Thanks!'''

                        self.send_sms(smstext, mobile_phone)
                        self.send_sms(smstext, '+4542788282') #Change to mobile_phone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        dbman.delay_warn(self.databasePath, orderno, 'yes')        
             
    def count_order_in_timeFrame(self, date, timeframe, order_type):
        if order_type == 'delivery':
            #Query the data base of orders within same time frame
            import sqlite3
            conn = sqlite3.Connection(self.databasePath)
            c = conn.cursor()
            mystr = f'''SELECT ORDERNO FROM order_execution WHERE DATE = {date} AND TIME = {timeframe} '''
            c.execute(mystr)
            data = c.fetchall()
        
    def logging(self, level, message):
        #Instantiate logging
        logging.basicConfig(filename = 'log.txt', 
        filemode = 'a', 
        level = logging.DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s')
        if level == 'debug':
            logging.debug(message)
        
        if level == 'info':
            logging.info(message)
        
        if level == 'warning':
            logging.warning(message)

        if level == 'error':
            logging.error(message)
        
        if level == 'critical':
            logging.critical(message)

    def send_sms(self, smstext, send_to):
        '''
        Send a delay sms with sms text to the number (send_to)
        '''
        #Prepare the phone number
        #First remove empty white spaces in string 
        send_to = send_to.replace(' ','')
        if len(send_to) == 8:
            send_to = f'+45{send_to}'

        #Send SMS
        client = Client(self.sms_cred['account_sid'], self.sms_cred['auth_token'])
        message = client.messages.create(body= smstext, to= send_to, from_ = '+4592454888')

#Upon start
while True:
    #Define which store to use
    store = 'DK'
    mo = ManageOrder(switch = store) #Instantiate the store
    status, amount = mo.incomeStatus(switch = store) #get amount earning from this store at current month
    print(f'Amount for this month in {store} {amount} dkk')
    
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
    mohk = ManageOrder(switch = store) #Instantiate the store
    status, amount = mohk.incomeStatus(switch = store) #get amount earning from this store at current month
    print(f'Amount for this month in {store} {amount} dkk')
    
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
    time.sleep(5)

