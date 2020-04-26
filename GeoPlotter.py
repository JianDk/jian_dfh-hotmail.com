import sqlite3
import datetime
import folium

class GeoPlotter:
    def __init__(self, **kwargs):
        dbpath = kwargs['dbpath']
        self.home_latitude = kwargs['home_latitude']
        self.home_longitude = kwargs['home_longitude']
        self.deliveryRadius = kwargs['radius']

        #Get current date and time
        today_date = datetime.datetime.today().date()

        #Connect to the data base
        
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        mystr = '''SELECT ORDERNO, ORDER_TYPE, DATE, TIME FROM order_execution'''
        try:
            c.execute(mystr)
        except:
            self.m = self.map_init(home_lat = self.home_latitude, home_lng = self.home_longitude, radius = self.deliveryRadius)
            self.m.save('DeliveryMap.html')
            return

        data = c.fetchall()
        conn.close()

        #Filter out the delivery orders together with their time and date
        DeliveryOrder = [(i[0], i[2], i[3],) for i in data if i[1] == 'Delivery']

        #From these orders check, which of them is for delivery today
        timeformat = '%Y-%m-%d %I:%M %p'
        plotlist = list()
        for item in DeliveryOrder:
            if datetime.datetime.strptime(item[1], '%d/%m/%Y').date() == today_date:

                #get current time
                now = datetime.datetime.now()

                #Get start and end time for the delivery Order
                tmp = item[2].split('-')
                start_str = str(today_date) + ' ' + tmp[0].strip()
                start = datetime.datetime.strptime(start_str, timeformat) 
                print(tmp)
                end_str = str(today_date) + ' ' + tmp[1].strip()
                end = datetime.datetime.strptime(end_str, timeformat)

                executionStart = start - datetime.timedelta(minutes=30) 

                nextslot_end = start + datetime.timedelta(minutes=60) #no need to write nextslot start since it is same as end

                past_start = start - datetime.timedelta(minutes=60)
                
                plotdict = dict()
                if past_start <= now <= executionStart:
                    plotdict['markerColor'] = 'green'
                    plotdict['executionTime'] = item[2]
                    plotdict['orderno'] = item[0]
                    plotlist.append(plotdict)

                if executionStart < now <= start:
                    plotdict['markerColor'] = 'orange'
                    plotdict['executionTime'] = item[2]
                    plotdict['orderno'] = item[0]
                    plotlist.append(plotdict)

                if start < now < end:
                    plotdict['markerColor'] = 'red'
                    plotdict['executionTime'] = item[2]
                    plotdict['orderno'] = item[0]
                    plotlist.append(plotdict)
                
                if end <= now <= nextslot_end:
                    plotdict['markerColor'] = 'white'
                    plotdict['executionTime'] = item[2]
                    plotdict['orderno'] = item[0]
                    plotlist.append(plotdict)

        self.m = self.map_init(home_lat = self.home_latitude, home_lng = self.home_longitude, radius = self.deliveryRadius)
        
        if not plotlist:
            #Generate an empty map
            self.m.save('DeliveryMap.html')

        else: # there is something to plot in the map
            #Get latitude and longitude along with customer information

            for item in plotlist:
                conn = sqlite3.Connection(dbpath)
                c = conn.cursor()
                c.execute(f'''SELECT * FROM customer WHERE ORDERNO = "{item['orderno']}"''')
                data = c.fetchone()
                conn.close()
                item['latitude'] = data[4]
                item['longitude'] = data[5]
                item['name'] = data[1]
                item['address'] = data[2]
                item['contact'] = data[3]

                self.m = self.map_addMarker(item = item)

            self.m.save('DeliveryMap.html')
    
    def map_init(self, **kwargs):
        #Centers the map
        locationHome = [kwargs['home_lat'], kwargs['home_lng']]
        self.m = folium.Map(location = locationHome,
        zoom_start=12)
        
        #Generate the home marker
        folium.Marker(location = locationHome,
            popup = 'Hidden Dimsum', 
            icon = folium.Icon(color = 'black')).add_to(self.m)
        
        #Generate the circle of delivery radius
        folium.Circle(radius= kwargs['radius'],
        location = locationHome,
        popup='',
        fill=False).add_to(self.m)
        return self.m

    def map_addMarker(self, item):
        location = [item['latitude'], item['longitude']]
        popup = f'''<strong>{item['name']}</strong>
        <br>{item['executionTime']} 
        <br>{item['address']}<br>{item['contact']}'''
        folium.Marker(location = location, popup = popup, icon = folium.Icon(color = item['markerColor'])).add_to(self.m)
        return self.m

        
