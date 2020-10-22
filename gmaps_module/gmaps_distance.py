import os

from googlemaps.distance_matrix import distance_matrix
from googlemaps.geocoding import geocode

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_bot.settings")

import django

django.setup()

from app.models import Restaurant
import googlemaps

gmaps = googlemaps.Client(key='AIzaSyDm1WHPoV2ZeGlMQHf6RJtjAnNCG_-ChAc')

restaurants = Restaurant.objects.all()[0:2]

all_links = [link.address for link in restaurants]
# для тестов: 30.392048 59.983499

for i in all_links:
    print(i)
    lat = geocode(client=gmaps, address=i)[0]['geometry']['location']['lat']
    lng = geocode(client=gmaps, address=i)[0]['geometry']['location']['lng']
    coords = [str(lat), str(lng)]
    destination = "".join(coords)

    print(distance_matrix(client=gmaps, origins='59.943984 30.355459', destinations=i)['rows'][0]['elements'][0]['distance']['text'])
