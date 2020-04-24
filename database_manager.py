import sqlite3
def createDB(path_db):
    '''
    Setting up the sqlite3 data base table columns. Following tables will be created

    customer: containing customer related data
    order : containing all orders from all customer
    order execution : containing type of order (delivery or pickup) and when it is expected to be fullfilled
    '''
    conn = sqlite3.connect(path_db)

    conn.execute('''CREATE TABLE customer
    (ORDERNO INT PRIMARY KEY     NOT NULL,
    NAME            TEXT,
    ADDRESS         TEXT,
    PHONE           TEXT,
    EMAIL           TEXT,
    GPS_LATITUDE    TEXT,
    GPS_LONGITUDE   TEXT)''')

    conn.execute('''CREATE TABLE items
    (ID_ROW     INT     PRIMARY KEY,
    ITEM        TEXT       NOT NULL,
    AMOUNT      INT     NOT NULL,
    UNIT_PRICE       REAL    NOT NULL,
    ORDERNO     INT     NOT NULL)''')

    conn.execute('''CREATE TABLE order_execution
    (ORDERNO INT PRIMARY KEY     NOT NULL,
    ID              INT         NOT NULL,
    NAME            TEXT        NOT NULL,
    ORDER_TYPE      TEXT       NOT NULL,
    DATE            TEXT        NOT NULL,
    TIME            TEXT       NOT NULL,
    CREATED_AT      TEXT        NOT NULL,
    DELAY_WARN      TEXT       NOT NULL,
    PRINT_STATUS    TEXT       NOT NULL,
    FULFILL_AND_CLOSE TEXT        NOT NULL,
    NOTE            TEXT)''')

    conn.commit()
    conn.close()

def insert_orderList_to_DB(path_db, orderList):
    conn = sqlite3.connect(path_db)
    
    #insert to customer table
    for item in orderList:
        #insert to customer table
        #check if deliverAddress exists
        if 'deliverAddress' in item:
            mystr = f'''INSERT INTO customer \
            (ORDERNO, NAME, ADDRESS, CONTACT, GPS_LATITUDE, GPS_LONGITUDE) \
            VALUES ({int(item['ShopifyOrderNo'])}, '{item['guestName']}', '{item['deliverAddress']}', '{item['contact']}', \
            {item['latitude']}, {item['longitude']});'''
        else:
            mystr = f'''INSERT INTO customer \
            (ORDERNO, NAME, CONTACT) VALUES ({int(item['ShopifyOrderNo'])}, '{item['guestName']}', '{item['contact']}');'''
            
        conn.execute(mystr)

        #Insert into items
        tmp = list(zip(item['itemName'], item['amount'], item['price']))
        for i in tmp:
            mystr = f'''INSERT INTO items \
                (ID_ROW, ITEM, AMOUNT, UNIT_PRICE, ORDERNO) \
                VALUES (NULL, '{i[0]}', {i[1]}, {i[2]}, {item['ShopifyOrderNo']})'''
            
            conn.execute(mystr)
        
        #Insert into order_execution
        mystr = f'''INSERT INTO order_execution \
            (ORDERNO, ORDER_TYPE, DATE, TIME, PRINT_STATUS, ORDER_DELIVERED, PAYMENT_RECEIVED) \
            VALUES ({item['ShopifyOrderNo']}, \
                '{item['deliveryMethod']}', \
                '{item['ExecutionDate']}', \
                '{item['ExecutionTime']}', \
                'no', \
                'no', \
                'no')'''
        conn.execute(mystr)

    conn.commit()
    conn.close()

def get_existingOrderNo(path_db):
    conn = sqlite3.Connection(path_db)
    c = conn.cursor()
    try:
        c = c.execute('''SELECT ORDERNO FROM order_execution''')
    except:
        print('get_existingOrderNo data base cannot select orderno from data base')
        return
    orderno = c.fetchall()
    conn.close()
    orderno = [i[0] for i in orderno]
    return orderno

def get_customer(path_db, orderno):
    '''returns all customer information from the customer table '''
    conn = sqlite3.Connection(path_db)
    c = conn.cursor()
    mystr = f'''SELECT * FROM customer WHERE ORDERNO = {orderno}'''
    c.execute(mystr)
    customer = c.fetchone()
    conn.close()
    return customer

def get_incomplete_orders(path_db):
    '''
    Get a list of orderno and shopify order id that are not yet fulfilled and closed
    '''
    conn = sqlite3.Connection(path_db)
    c = conn.cursor()
    mystr = '''SELECT ORDERNO, ID, ORDER_TYPE, DATE, TIME, FULFILL_AND_CLOSE \
        FROM order_execution WHERE FULFILL_AND_CLOSE = 'no' OR FULFILL_AND_CLOSE = 'now' '''
    c.execute(mystr)
    data = c.fetchall()
    return data

def insert_orders_to_database(path_db, orders):
    conn = sqlite3.Connection(path_db)
    c = conn.cursor()
    #Loop over all orders
    for item in orders:
        orderno = int(item['name'].split('#')[1])

        #Get customer information
        customer_name = item['shipping_address']['name']
        if not customer_name:
            customer_name = 'None'
        
        phone = item['shipping_address']['phone']
        if not phone:
            phone = 'None'

        email = item['email']
        if not email:
            email =  'None'

        latitude = item['shipping_address']['latitude']
        if not latitude:
            latitude = 'None'

        longitude = item['shipping_address']['longitude']
        if not longitude:
            longitude = 'None'

        address = [item['shipping_address']['address1'], item['shipping_address']['address2'], item['shipping_address']['zip'], item['shipping_address']['city']]
        address = ', '.join(i for i in address if i)

        if not address:
            address = 'None'

        #Check if orderno exists in the data base
        status = orderno_exists(path_db, orderno, 'customer')
        if status is False:
            #Update into table start with customer
            mystr = f'''INSERT INTO customer (ORDERNO, NAME, ADDRESS, PHONE, EMAIL, GPS_LATITUDE, GPS_LONGITUDE) \
                VALUES ({orderno}, '{customer_name}', '{address}', '{phone}', '{email}', '{latitude}', '{longitude}')'''

            conn = sqlite3.Connection(path_db)
            c = conn.cursor()
            c.execute(mystr)
            conn.commit()
            conn.close()

            #Update into table items
            for dish in item['line_items']:
                if not dish['variant_title']:
                    item_name = dish['title']
                else:
                    item_name = dish['variant_title']
                
                amount = int(dish['quantity'])
                unit_price = float(dish['price'])
                
                mystr =  f'''INSERT INTO items \
                    (ID_ROW, ITEM, AMOUNT, UNIT_PRICE, ORDERNO) \
                    VALUES (NULL, '{item_name}', {amount}, {unit_price}, {orderno})'''
                
                conn = sqlite3.Connection(path_db)
                c = conn.execute(mystr)
                conn.commit()
                conn.close()

            #Update into order_execution
            order_type = item['note_attributes'][0]['value']
            date = item['note_attributes'][2]['value']
            time = item['note_attributes'][3]['value']
            created_at = item['created_at']
            order_id = int(item['id'])
            delay_warn = "no" #Default is no
            print_status = "no"
            #Check if item is fulfilled if not
            if item['fulfillment_status'] == 'unfulfilled':
                fulfill_and_close = "no"
            elif item['fulfillment_status'] == 'fulfilled' and item['financial_status'] == 'paid':
                #check if item is closed
                fulfill_and_close = "yes"
                print_status = "yes"
            else:
                fulfill_and_close = "no"
            
            note = item['note']
            if not note:
                note = 'None'
            else:
                note = note.replace('\"','\'')

            mystr = f'''INSERT INTO order_execution \
            (ORDERNO, ID, NAME, ORDER_TYPE, DATE, TIME, CREATED_AT, DELAY_WARN, PRINT_STATUS, FULFILL_AND_CLOSE, NOTE) \
            VALUES ({orderno}, \
                {order_id}, \
                '{customer_name}', \
                '{order_type}', \
                '{date}', \
                '{time}', \
                '{created_at}', \
                '{delay_warn}', \
                '{print_status}', \
                '{fulfill_and_close}', \
                "{note}")'''
            
            conn = sqlite3.Connection(path_db)
            c = conn.cursor()
            c.execute(mystr)
            conn.commit()
            conn.close()

def orderno_exists(path_db, orderno, tablename):
    '''
    Check if orderno exists in the data base given orderno as int and tablename as str. 
    '''
    conn = sqlite3.Connection(path_db)
    c = conn.cursor()
    c.execute(f'''SELECT ORDERNO from {tablename} WHERE ORDERNO = {orderno} ''')
    data = c.fetchone()
    conn.close()
    if not data:
        return False
    else:
        return True

def setPrintedStatus(path_db, orderno, status):
    '''sets the order_execution table the printed status to either yes or no, depending on the status string. order is the orderno'''
    conn = sqlite3.Connection(path_db)
    c = conn.cursor()
    mystr = 'UPDATE order_execution SET PRINT_STATUS = ? WHERE ORDERNO = ?'
    c.execute(mystr, (status, orderno))
    conn.commit()
    conn.close()
   
