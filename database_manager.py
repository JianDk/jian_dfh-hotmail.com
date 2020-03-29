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
    NAME       TEXT,
    ADDRESS         TEXT,
    CONTACT         TEXT,
    GPS_LATITUDE    REAL,
    GPS_LONGITUDE  REAL)''')

    conn.execute('''CREATE TABLE items
    (ID_ROW     INT     PRIMARY KEY,
    ITEM        TEXT       NOT NULL,
    AMOUNT      INT     NOT NULL,
    UNIT_PRICE       REAL    NOT NULL,
    ORDERNO     INT     NOT NULL)''')

    conn.execute('''CREATE TABLE order_execution
    (ORDERNO INT PRIMARY KEY     NOT NULL,
    ORDER_TYPE      TEXT       NOT NULL,
    DATE            TEXT        NOT NULL,
    TIME            TEXT       NOT NULL,
    PRINT_STATUS    TEXT       NOT NULL,
    ORDER_DELIVERED TEXT        NOT NULL,
    PAYMENT_RECEIVED TEXT       NOT NULL)''')

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


   
