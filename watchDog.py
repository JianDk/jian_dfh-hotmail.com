import datetime
import json 
from twilio.rest import Client
import time

class setWatchDog:
    
    def __init__(self, minutes_limit, timestampFilePath):
        self.timestampFilePath = timestampFilePath
        self.minutes_limit = minutes_limit
        self.alarm = False

        while True:
            #Read in the last stamped date time
            #Read the time
            with open(self.timestampFilePath,'r') as file:
                self.data = json.load(file)
            
            print(self.data)

            self.alarm = self.data['alarmStatus']

            #turn last time stamp to a date time object and get the elapsed time
            lastTimeStamp = datetime.datetime.strptime(self.data['time'], '%Y-%m-%d %H:%M:%S')
            now = datetime.datetime.now()
            minutes_elapsed = (now - lastTimeStamp).seconds / 60
        
            if (minutes_elapsed > minutes_limit) and self.alarm is False:
                #Create text and send sms
                sms_text = f'Shopify script er stoppet siden {lastTimeStamp}'
                #Send alarm. Note set alarm to true is built into the send_sms method
                self.send_sms(sms_text, '+4542788282')
                self.send_sms(sms_text, '+4560732838')
                self.data['alarmStatus'] = True
                self.setAlarmTrue(self.data)
        
            time.sleep(10)

    def send_sms(self, smstext, send_to):
        '''
        Send a delay sms with sms text to the number (send_to)
        '''
        #import the credientials
        with open('twilio_crediential.txt','r') as file:
            sms_cred = json.load(file)

        #Prepare the phone number
        #First remove empty white spaces in string 
        send_to = send_to.replace(' ','')
        if len(send_to) == 8:
            send_to = f'+45{send_to}'

        #Send SMS
        client = Client(sms_cred['account_sid'], sms_cred['auth_token'])
        message = client.messages.create(body= smstext, to= send_to, from_ = '+4592454888')
    
    def setAlarmTrue(self, data):
        #Set alarm status to True signifying that system break down is noted and appropriate actions taken. 

        with open(self.timestampFilePath, 'w') as file:
            json.dump(data, file)
    
        