import sqlite3
import datetime
from ShopifyPrinter_win10 import Printer as printer
import database_manager as dbman
import json

class printOrder:
    def __init__(self, dbpath, printerParam):
        #Get translation dict
        with open('Shopify_item2print.txt') as f:
            translation = json.load(f)

        #Connect to the data base
        conn = sqlite3.Connection(dbpath)
        c = conn.cursor()
        #check from order_execution table if any orders are within print date and time
        mystr = '''SELECT ORDERNO, ORDER_TYPE, DATE, TIME, PRINT_STATUS FROM order_execution WHERE PRINT_STATUS = 'no' '''
        c.execute(mystr)
        data = c.fetchall()

        #Also get data from which sqldata base was manually set to print now
        mystr = '''SELECT ORDERNO, ORDER_TYPE, DATE, TIME, PRINT_STATUS FROM order_execution WHERE PRINT_STATUS = 'print now' '''
        c.execute(mystr)
        data2 = c.fetchall()
        conn.close()
        
        #if there is something we need to print now
        if data2:
            for item in data2:
                printdict = self.add_executionInfo_to_Printdict(item)

                #Get items in the order
                conn = sqlite3.Connection(dbpath)
                c = conn.cursor()
                mystr = f'''SELECT ITEM, AMOUNT, UNIT_PRICE, ORDERNO FROM items WHERE ORDERNO = {printdict['orderno']} '''
                c.execute(mystr)
                data2 = c.fetchall()
                printdict['items'] = data2

                #Get customer information
                customer = dbman.get_customer(dbpath, printdict['orderno'])
                printdict = self.add_customerInfo_to_printdict(customer, printdict)
                
                #connect to printer and print twice one to kitchen and one to host 
                p = printer(printerParam['printerNear'])
                p.printDelivery(printdict, translation)
                p = printer(printerParam['printerFar'])
                p.printDelivery(printdict, translation)
                
                #After printing, the printed status in data base will be switched to 'yes'
                dbman.setPrintedStatus(dbpath, printdict['orderno'], 'yes')
                
        if not data:
            print('no printable orders')
            return

        for item in data:
            #check first if date is today
            dateformat = '%d/%m/%Y'
            orderDate = datetime.datetime.strptime(item[2], dateformat)
            todayDate = datetime.datetime.today().date()

            if orderDate.date() == todayDate: #within date scope for printing. Check if within time scope as well
                #execution time 
                tmp = item[3].split('-')
                startstr = str(todayDate) + ' ' + tmp[0].strip()
                timeformat = '%Y-%m-%d %I:%M %p'
                
                start = datetime.datetime.strptime(startstr, timeformat)
                
                executionStart = start - datetime.timedelta(minutes=60)

                now = datetime.datetime.now()

                if now >= executionStart:
                    printdict =  self.add_executionInfo_to_Printdict(item)

                    #Get items in the order
                    conn = sqlite3.Connection(dbpath)
                    c = conn.cursor()
                    mystr = f'''SELECT ITEM, AMOUNT, UNIT_PRICE, ORDERNO FROM items WHERE ORDERNO = {printdict['orderno']} '''
                    c.execute(mystr)
                    data2 = c.fetchall()
                    printdict['items'] = data2

                    #Get customer information
                    customer = dbman.get_customer(dbpath, printdict['orderno'])
                    printdict = self.add_customerInfo_to_printdict(customer, printdict)
                    
                    #connect to printer and print twice one to kitchen and one to host 
                    p = printer(printerParam['printerNear'])
                    p.printDelivery(printdict, translation)
                    p = printer(printerParam['printerFar'])
                    p.printDelivery(printdict, translation)
                    
                    #After printing, the printed status in data base will be switched to 'yes'
                    dbman.setPrintedStatus(dbpath, printdict['orderno'], 'yes')

    def add_executionInfo_to_Printdict(self, item):
        '''
        adds execution table information from the sql to print dict
        '''
        printdict =  dict()
        printdict['deliveryType'] = item[1]
        printdict['executionTime'] = item[3]
        printdict['orderno'] = item[0]
        return printdict

    def add_customerInfo_to_printdict(self, customer, printdict):
        printdict['name'] = customer[1]
        printdict['address'] = customer[2]
        printdict['contact'] = customer[3]
        printdict['latitude'] = customer[4]
        printdict['longitude'] = customer[5]
        return printdict
        

                    