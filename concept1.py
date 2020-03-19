
import imaplib
import email
import re
#Connect
#con = imaplib.IMAP4_SSL(host = "imap.gigahost.dk", port = 993)
con = imaplib.IMAP4_SSL(host = "imap-mail.outlook.com")

#login
#con.login(user = "kontakt@dimsum.dk", password = "DimSum2018")
con.login(user = "jian_dfh@hotmail.com", password = "PASSport1")

#Select inbox
con.select("INBOX")

#set the date
date = "17-Mar-2020"
result, mailid_from = con.search(None, '(FROM "kontakt@dimsum.dk")')
if result != 'OK':
    print('No mail from sender')

result, mailid_since = con.search(None, '(SINCE "16-Mar-2020")')

#Find the common ids to include both from and date
mailid_from = mailid_from[0].split()
mailid_since = mailid_since[0].split()
mail_id = set(mailid_from).intersection(set(mailid_since))

#Fetch the emails with a loop
OrderList = list()

for item in mail_id:
    #Get email data
    result, data = con.fetch(item,'(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    #get subject
    msg_subject = msg['Subject']
    print(msg_subject)
    #decode
    print('decode')
    msg_subject = email.header.decode_header(msg_subject)
    print(msg_subject)
    if msg_subject[0][1] != None:
        print('decoded message')
        msg_subject = msg_subject[0][0].decode(msg_subject[0][1])
    else:
        msg_subject = msg_subject[0][0]
    
    #Do a check to see if subject match delivery
    if "[Hidden Dimsum Delivery Take Away] Order #" in msg_subject:
        Order = dict()
        Order['mail_id'] = item
        Order['Subject'] = msg_subject
        #get person's name who placed the order

        print(Order)
        print('wait')