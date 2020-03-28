#latitude': 55.7294575, 'longitude': 12.5380862
import gmplot
#Center the map around store
gmap1 = gmplot.GoogleMapPlotter(55.677063, 12.573435, 12, apikey= "AIzaSyCmczCD01h-5DpcaV3TLtg9bneSro8arDE") 
gmap1.marker(55.7294575, 12.5380862, title ='this is my home')
gmap1.marker(55.72, 12.53, title = 'another location')
gmap1.draw("mymap.html")