import requests
api_key = 'AIzaSyCOj6maIO2FkgdAKNWZOI72Zxtwe-nkVBM'
address = 'Ellemosevej 35, 2900 Hellerup, Denmark'
url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'

with requests.Session() as r:
    resp = r.get(url)

resp = resp.json()['results'][0]['geometry']['location']
latitude = resp['lat']
longtitude = resp['lng']

print(resp)
