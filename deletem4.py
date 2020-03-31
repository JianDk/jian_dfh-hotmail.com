import imaplib 
import email
import sys
import datetime
import sqlite3

#Clean up in mail box
mail = 'kontakt@dimsum.dk'
host = 'imap.gigahost.dk'
password = 'DimSum2018'
port = 993

connection = imaplib.IMAP4_SSL(host = host, port = port)
connection.login(user = mail, password = password)
connection.select('INBOX')

#Perform a filter to search for emails from secomapp
result, mailid_from = connection.search(None, f'(FROM "notifications-noreply@secomapp.com")')

if result != 'OK':
    sys.exit("No emails from Secomapp stop")
    connection.close()
    connection.logout()

mailid_from = mailid_from[0].split()

#this sweep will remove all emails that are earlier than today
today_date = datetime.datetime.today().date()

for mailid in mailid_from:
    #Get email data
    result, data = connection.fetch(mailid, '(RFC822)')

    msg = email.message_from_bytes(data[0][1])

    #get subject title
    msg_subject = msg['Subject']

    #decode
    msg_subject = email.header.decode_header(msg_subject)
    msg_subject = msg_subject[0][0]
    
    #Chek if the email header is a delivery or pickup email
    if '[Store Pickup Notification] Order' in msg_subject:
        #Get the date and time for store pickup
        pickupDate = msg_subject.split('\r\n store')[1].split('-')[0].strip()
        pickupDate = datetime.datetime.strptime(pickupDate, '%d/%m/%Y').date()
        #Get time for store pickup
        pickupTime = msg_subject.split('-')[1].strip().split('.')[0]
        pickupTime = datetime.datetime.strptime(pickupTime, '%H:%M').strftime('%I:%M %p')
        #Get order no
        orderno = int(msg_subject.split('#')[1].strip().split('will')[0].strip())
        #Check if orderno already exists in current database together with date and time
        conn = sqlite3.Connection('orderDB.db')
        c = conn.cursor()
        c.execute(f'''SELECT ORDERNO, ORDER_TYPE, DATE, TIME FROM order_execution WHERE ORDERNO = {orderno}''')
        data_db = c.fetchone()

        if data_db \
            and data_db[1] == 'Store Pickup' \
            and datetime.datetime.strptime(data_db[2],'%d/%m/%Y').date() == pickupDate and \
            data_db[3] == pickupTime:
            
            connection.store(mailid, '+FLAGS', '\\Deleted')

            print('email pickup found and marked for delete')
    
    if '[Local Delivery Notification] Order #' in msg_subject:
        print(msg_subject)
    

connection.expunge()


#Close the connection
connection.close()
connection.logout()