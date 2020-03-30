import sqlite3
import datetime
from ShopifyPrinter_win10 import Printer as printer
import database_manager as dbman

class printOrder:
    def __init__(self, dbpath, printerParam):
        #Connect to the data base
        conn = sqlite3.Connection(dbpath)
        c = conn.cursor()
        #check from order_execution table if any orders are within print date and time
        mystr = '''SELECT ORDERNO, ORDER_TYPE, DATE, TIME, PRINT_STATUS FROM order_execution WHERE PRINT_STATUS = 'no' '''
        c.execute(mystr)
        data = c.fetchall()
        conn.close()
        
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
                
                executionStart = start - datetime.timedelta(minutes=30)

                now = datetime.datetime.now()

                if now >= executionStart:
                    printdict =  dict()
                    printdict['deliveryType'] = item[1]
                    printdict['executionTime'] = item[3]
                    printdict['orderno'] = item[0]

                    #Get items in the order
                    conn = sqlite3.Connection(dbpath)
                    c = conn.cursor()
                    mystr = f'''SELECT ITEM, AMOUNT, UNIT_PRICE, ORDERNO FROM items WHERE ORDERNO = {printdict['orderno']} '''
                    c.execute(mystr)
                    data2 = c.fetchall()
                    printdict['items'] = data2

                    #Get customer information
                    customer = dbman.get_customer(dbpath, printdict['orderno'])
                    print(customer)
                    printdict['name'] = customer[1]
                    printdict['address'] = customer[2]
                    printdict['contact'] = customer[3]
                    printdict['latitude'] = customer[4]
                    printdict['longitude'] = customer[5]
                    
                    #connect to printer and print twice one to kitchen and one to host 
                    p = printer(printerParam)
                    p.printDelivery(printdict)
                    p = printer(printerParam)
                    p.printDelivery(printdict)
                    
                    #After printing, the printed status in data base will be switched to 'yes'
                    dbman.setPrintedStatus(dbpath, printdict['orderno'], 'yes')

                    