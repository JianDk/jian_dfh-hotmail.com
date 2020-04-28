import imaplib 
import email
import sys
import datetime

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
            
        connection.store(mailid, '+FLAGS', '\\Deleted')
        print('email pickup found and marked for delete')
    
    if '[Local Delivery Notification] Order #' in msg_subject:
        #get orderno, date and delivery time
        connection.store(mailid, '+FLAGS', '\\Deleted')
        print('mark Delivery email for deletion')

connection.expunge()

#Perform a filter to search for emails from HK mail account
result, mailid_from = connection.search(None, f'(FROM "alexanderydesign@gmail.com")')
mailid_from = mailid_from[0].split()

for mailid in mailid_from:
    #Get email data
    result, data = connection.fetch(mailid, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])

    #get subject title
    msg_subject = msg['Subject']

    #decode
    msg_subject = email.header.decode_header(msg_subject)
    msg_subject = msg_subject[0][0]
    
    try:
        msg_subject = msg_subject.decode()
    except:
        pass

    if '[Hidden Dimsum] Order #' in msg_subject:
        connection.store(mailid, '+FLAGS', '\\Deleted')
        print('Hidden Dimsum order email from HK deleted')

connection.expunge()


#Close the connection
connection.close()
connection.logout()