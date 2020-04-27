import json
from twilio.rest import Client

#Start by importing twilio credientials
with open('twilio_crediential.txt') as f:
    cred = json.load(f)

client = Client(cred['account_sid'], cred['auth_token'])
message = client.messages.create(body="this is a test with æ,ø,å", to='+4542788282', from_ = '+4592454888')
