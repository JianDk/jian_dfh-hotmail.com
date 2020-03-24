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
    FIRSTNAME       TEXT,
    LASTNAME        TEXT,
    ADDRESS         CHAR(150),
    GPS_LATITUDE    REAL,
    GPS_LONGITUDE  REAL,);''')

    conn.execute('''CREATE TABLE order
    (ID_ROW     INT     PRIMARY KEY     NOT NULL,
    ITEM        CHAR(150)       NOT NULL,
    AMOUNT      INT     NOT NULL,
    UNIT_PRICE       REAL    NOT NULL,
    ORDERNO     INT     NOT NULL,);''')

    conn.execute('''CREATE TABLE order_execution
    (ORDERNO INT PRIMARY KEY     NOT NULL,
    ORDER_TYPE      CHAR(150)       NOT NULL,
    TIME            CHAR(150)       NOT NULL,
    PRINT_STATUS    CHAR(50)        NOT NULL,
    ORDER_DELIVERED CHAR(50)        NOT NULL,
    PAYMENT_RECEIVED CHAR(50)       NOT NULL,);''')

    conn.commit()
    conn.close()

