import datetime
timeframe = '13:00'
if 'PM' not in timeframe and 'AM' not in timeframe:
    timeframe = datetime.datetime.strptime(timeframe, "%H:%M")
    timeframe = timeframe.strftime("%I:%M %p")
    print('here')