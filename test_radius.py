import folium
m = folium.Map(location = [55.677063, 12.573435], zoom_start = 12) 
folium.Marker(location = [55.677063, 12.573435], popup = 'Hidden Dimsum', icon = folium.Icon(color = 'black')).add_to(m)

radius = [5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000]
for r in radius:
        
    folium.Circle(
        radius = r,
        location= [55.677063, 12.573435],
        popup='',
        fill=False,
    ).add_to(m)

m.save('map.html')