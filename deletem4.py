import imaplib 
import email
import sys

#Clean up in mail box
email = 'kontakt@dimsum.dk'
host = 'imap.gigahost.dk'
password = 'DimSum2018'
port = 993

connection = imaplib.IMAP4_SSL(host = host, port = port)
connection.login(user = email, password = password)
connection.select('INBOX')

#Perform a filter to search for emails from secomapp
result, mailid_from = connection.search(None, f'(FROM "notifications-noreply@secomapp.com")')

if result != 'OK':
    sys.exit("No emails from Secomapp stop")

for mailid in mailid_from:
    print(mailid)
    connection.close()
    connection.logout()


#Close the connection
connection.close()
connection.logout()