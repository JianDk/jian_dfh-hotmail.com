import folium
import time

m = folium.Map(location = [55.677063, 12.573435], zoom_start = 12) 

folium.Marker(location = [55.677063, 12.573435], popup = 'Hidden Dimsum', icon = folium.Icon(color = 'black')).add_to(m)

folium.Circle(
    radius=11000,
    location= [55.677063, 12.573435],
    popup='',
    fill=False,
).add_to(m)

tooltip = 'click'
marker = folium.Marker([55.7294575, 12.5380862], popup='<strong>Frederik</strong>', tooltip=tooltip)
marker.add_to(m)
m.save('map.html') 
