import requests
api_key="AIzaSyCmczCD01h-5DpcaV3TLtg9bneSro8arDE"
address = 'Emdrupvej 113, 3.3, 2400 København'

url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
data = requests.get(url = url)
if data.status_code != 200:
    print('place not existent')

data = data.json()['results']
print(data)
