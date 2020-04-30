import sqlite3
import datetime

# Mockup information
order_type = 'delivery'
delay_date = '25/04/2020'
delay_time = '6:00 PM - 6:30 PM'
created_at = '2020-04-25T17:59:00+02:00'
delay_warn = 'no'
databasepath = 'orderDBDK.db'

def created_at_to_datetime(created_at):
    '''
    converts created_at to datetime object without daylight saving awareness. Input created_at 
    as string in format "%Y-%m-%dT%H:%M:%S%z"
    '''
    
    created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z")
    created_at = created_at.replace(tzinfo=None)
    return created_at

def convert_pickup_datetime(datestr, timestr):
    '''
    convert shopify pickup date and time to datetime format
    '''
    datestr = datestr + '-' + timestr
    timeformat = '%d/%m/%Y-%H:%M'
    date_and_time = datetime.datetime.strptime(datestr, timeformat)
    return date_and_time

def convert_delivery_datetime(datestr, timestr, option):
    '''
    convert shopify delivery date and time to datetime format
    datestr is given as e.g. 23/04/2020 
    timestr is given as e.g. 6:30 PM - 7:30 PM
    option can either be start_time or end_time provided as string. If start time, the datetime will be formed by using 
    6:30 PM as start time as in this example. If end_time datetime will be formed using 7:30 PM as in this example.
    '''
    #Split the time to start time and end time
    timestr = timestr.split('-')
    start_time = timestr[0].strip()
    end_time = timestr[1].strip()
    
    timeformat = '%d/%m/%Y-%I:%M %p'
    if option == 'start_time':
        timestr = datestr + '-' + start_time
        date_and_time = datetime.datetime.strptime(timestr, timeformat)
    
    if option == 'end_time':
        timestr = datestr + '-' + end_time
        date_and_time = datetime.datetime.strptime(timestr, timeformat)

    return date_and_time            

if order_type == 'delivery' and delay_warn == 'no':
    #Convert to datetime
    created_at = created_at_to_datetime(created_at)
    start_delivery_time = convert_delivery_datetime(delay_date, delay_time, 'start_time')
    end_delivery_time = convert_delivery_datetime(delay_date, delay_time, 'end_time')
    
    #Evaluate how long in advance the order was created
    created_in_advance = (start_delivery_time - created_at).total_seconds() /60 #minutes customer created the order in advance
    
    if created_in_advance <= 0: #Greedy delivery time, where created at time is in the delivery time frame
        #no hesistation. Send delay sms
        print('SMS delay will be sent without further investigation. Delivery delay 30 min')

    if created_in_advance > 0 and created_in_advance < 30:
        #Check how many other orders we have in the requested delivery time
        tmp_timedelta = (end_delivery_time - start_delivery_time) / 2
        midpoint = start_delivery_time + tmp_timedelta

        print(midpoint)

        #Query the data base for all orders in the same date
        conn = sqlite3.Connection('orderDBDK.db')
        c = conn.cursor()
        mystr = f'''SELECT * FROM order_execution WHERE ORDER_TYPE = 'delivery' AND DATE = '{delay_date}'  '''  
        deliver_data = c.fetchall()

        mystr = f'''SELECT * FROM order_execution WHERE ORDER_TYPE = 'pickup' AND DATE = '{delay_date}' '''
        pickup_data = c.fetchall()
        conn.close()
        print('here is delivery data for delay_date')
        print(deliver_data)      
        print('here is pickup data for delay_date')
        print(pickup_data)