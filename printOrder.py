import sqlite3
import datetime

class printOrder:
    def __init__(self, dbpath):
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
                    print('should be printed')
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
                    print(data2)
                    #connect to printer and print
                    
                    print('write back to data base for print yes')
                    print(item)
                

        
    
printOrder('orderDB.db')