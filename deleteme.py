import sqlite3
conn = sqlite3.Connection('orderDBHK.db')
c = conn.cursor()
mystr = '''SELECT ORDERNO, ID, ORDER_TYPE, DATE, TIME, FULFILL_AND_CLOSE \
        FROM order_execution WHERE FULFILL_AND_CLOSE = 'no' OR FULFILL_AND_CLOSE = 'now' '''
c.execute(mystr)
data = c.fetchall()
conn.close()
print(data)