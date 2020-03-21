import imaplib 
import email
import datetime

class orderFromEmail:
    def __init__(self, **kwargs):
        self.email = kwargs['email']
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.password = kwargs['password']
    
    def EmailConnect(self):
        #Perform both the conenction and the user login
        #con = imaplib.IMAP4_SSL(host = "imap.gigahost.dk", port = 993)
        self.connection = imaplib.IMAP4_SSL(host = self.host, port = self.port)
        self.connection.login(user = self.email, password = self.password)

    def EmailFolderSelect(self, folderName):
        '''
        folderName is a string e.g. INBOX. Herafter the focus will be of all the emails in INBOX folder.
        '''
        self.connection.select(folderName)

    def searchOrderEmail(self, emailFrom):
        #Get today's date stamp
        today = datetime.datetime.today()
        today = today.strftime('%d-%b-%Y')

        #Perform a filter to search for all the emails from emailFrom from the date starting from today
        result, mailid_from = self.connection.search(None, f'(FROM "{emailFrom}")')

        if result != 'OK':
            print(f'No incoming emails from {emailFrom}')
            self.logoutClose()
            return
        
        #There exists emails from the sender. Check if any emails received from today
        result, mailid_since = self.connection.search(None, f'(SINCE "{today}")')
        if result != 'OK':
            print(f'Email from {emailFrom} exists, but none of these emails are from today!')
            self.logoutClose()
            return
        
        #Find the common ids to include both from sender and received date as today
        mailid_from = mailid_from[0].split()
        mailid_since = mailid_since[0].split()
        mail_id = set(mailid_from).intersection(set(mailid_since))

        #Fetch the emails from the common mail id in a loop. Note, the filter so far only searched for sender from today. Still need to assure that the mail type is a order mail
        OrderList = list()

        for mailid in mail_id:
            #Get email data
            result, data = self.connection.fetch(mailid, '(RFC822)')

            msg = email.message_from_bytes(data[0][1])

            #get subject title
            msg_subject = msg['Subject']

            #decode
            msg_subject = email.header.decode_header(msg_subject)
            print(msg_subject)

            if msg_subject[0][1] != None:
                msg_subject = msg_subject[0][0].decode(msg_subject[0][1])
            else:
                msg_subject = msg_subject[0][0]
            
            #Look for the selective tag in the subject field that is specific for a order email
            if '[Hidden Dimsum Delivery Take Away] Order #' in msg_subject:
                orderno, guestName = self.get_SubjectInfo(msg_subject)
                newOrder = dict()
                newOrder['ShopifyOrderNo'] = orderno
                newOrder['guestName'] = guestName

                #Extract email body information
                print('get the payload')
                for part in msg.walk():
                    print(part.get_content_type())
                    if part.get_content_type() == 'text/plain':
                        print('here is the content')
                        bodyText = part.get_payload()
                        print(type(bodyText))
                        print(bodyText)

                    print('\n')
                input('wait')
        
        self.logoutClose()
    
    def get_SubjectInfo(self, subject_title):
        orderno = subject_title.split(sep='#')[1].split()[0]
        guestName = subject_title.split(sep = 'placed by ')[1]
        return orderno, guestName
    
    def logoutClose(self):
        self.connection.close()
        self.connection.logout()


order = orderFromEmail(email = 'kontakt@dimsum.dk', host = 'imap.gigahost.dk', password = 'DimSum2018', port = 993)
order.EmailConnect()
order.EmailFolderSelect(folderName = 'INBOX')
order.searchOrderEmail('kontakt@dimsum.dk')