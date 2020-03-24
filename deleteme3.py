import sqlite3
conn = sqlite3.connect('helloworld.db')

conn.execute('''CREATE TABLE customer
(ORDERNO INT PRIMARY KEY     NOT NULL,
FIRSTNAME       TEXT,
LASTNAME        TEXT,
ADDRESS         CHAR(150),
GPS_LATITUDE    REAL,
GPS_LONGITUDE  REAL)''')

# conn.execute('''CREATE TABLE order
# (ID_ROW INT PRIMARY KEY NOT NULL,
# ITEM        CHAR(150)       NOT NULL,
# AMOUNT      INT     NOT NULL,
# UNIT_PRICE       REAL    NOT NULL,
# ORDERNO    INT     NOT NULL)''')

conn.execute('''CREATE TABLE order_execution
(ORDERNO INT PRIMARY KEY     NOT NULL,
ORDER_TYPE      CHAR(150)       NOT NULL,
TIME            CHAR(150)       NOT NULL,
PRINT_STATUS    CHAR(50)        NOT NULL,
ORDER_DELIVERED CHAR(50)        NOT NULL,
PAYMENT_RECEIVED CHAR(50)       NOT NULL)''')

conn.commit()
conn.close()