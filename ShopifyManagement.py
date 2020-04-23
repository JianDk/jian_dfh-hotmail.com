import datetime
import logging
import requests
from calendar import monthrange
import os
import database_manager as dbman

class ManageOrder:
    def __init__(self, **kwargs):
        self.API_VERSION = "2020-04"

        if kwargs['switch'] == 'DK':
            self.API_KEY = "f7bf71f3f3b7ce0a6f75863bdfccf53e"
            self.PASSWORD = "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"
            self.shop_url = "https://%s:%s@jian-xiong-wu.myshopify.com/admin/api/%s" % (self.API_KEY, self.PASSWORD, self.API_VERSION)
            self.databasePath = 'orderDBDK.db'

        if kwargs['switch'] == 'HK':
            self.API_KEY = "11d1233bd98782e8967a340918334686"
            self.PASSWORD = "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"
            self.shop_url = "https://%s:%s@alexanderystore.myshopify.com/admin/api/%s" % (self.API_KEY, self.PASSWORD, self.API_VERSION)
            self.databasePath = 'orderDBHK.db'
        
        #DEfine conversion rate from HKD to DKK
        self.conversion_HKD_DKK = 0.89

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
            if 'link' in resp.headers:
                print('True')

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


mo = ManageOrder(switch = 'HK')
#status, amount = mo.incomeStatus(switch = 'DK')
#status, account_switch = mo.account_switch_decision(maxIncome = 500000)
status, orders = mo.getOrders(orderType = 'closed')
mo.insert_orders_to_database(orders)
status, orders = mo.getOrders(orderType = 'open')
mo.insert_orders_to_database(orders)
