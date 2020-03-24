import sqlite3

conn = sqlite3.connect('test.db')

#Check if customer table already exists
c = conn.cursor()

c.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = "customer"''')

#If the customer table does not already exists, create one
if c.fetchone()[0] != 1:    
    conn.execute('''CREATE TABLE customer
    (ID INT PRIMARY KEY     NOT NULL,
    FIRSTNAME       TEXT,
    LASTNAME        TEXT,
    ADDRESS         CHAR(150),
    GPS_LATITUDE    REAL,
    GPS_LONGITUDE  REAL,
    ORDERNO         INT     NOT NULL
    );''')

#Insert some data into customer table
# conn.execute('''INSERT INTO customer (ID, FIRSTNAME, LASTNAME, ADDRESS, ORDERNO) \
#     VALUES (1000, 'Jian Xiong', 'Wu', 'Ellemosevej 35, 2900 Hellerup', 1000);''')

# conn.execute('''INSERT INTO customer (ID, FIRSTNAME, LASTNAME, GPS_LATITUDE, GPS_LONGITUDE, ORDERNO, ADDRESS) \
#     VALUES (1001, 'Min Hong', 'Mai', 22.3221, 23.2232, 1001, 'Emdrupvej 113, 3.3., 2400 København NV');''')

# conn.execute('''UPDATE customer SET GPS_LATITUDE = 23.2232, GPS_LONGITUDE = 213.2321 WHERE ID =1000''')

# conn.commit()

# conn.close()

#Check if a order no already exists in the data base
conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute('''SELECT ORDERNO FROM customer WHERE ORDERNO = 1000''')
for item in c.fetchall():
    print(item)

