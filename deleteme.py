import datetime
import re
title = '[Hidden Dimsum Delivery Take Away] Order #1047 placed by Theis Vangsbæk'
orderno = title.split(sep='#')[1].split()[0]
guestName = title.split(sep = 'placed by ')[1]


today = datetime.datetime.today()
today = today.strftime('%d-%b-%Y')
print(today)