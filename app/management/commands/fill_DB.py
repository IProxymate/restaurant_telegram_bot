import googlemaps
from django.core.management import BaseCommand
from googlemaps.geocoding import geocode

from app.models import Restaurant

gmaps = googlemaps.Client(key='AIzaSyDm1WHPoV2ZeGlMQHf6RJtjAnNCG_-ChAc')


class Command(BaseCommand):
    help = 'Simple command to add restaurant coordinates into the DB'

    def add_arguments(self, parser):
        parser.add_argument('--only_new', type=str)

    def handle(self, *args, **options):

        if options['only_new']:
            restaurants = Restaurant.objects.filter(coordinates__isnull=True)
        else:
            restaurants = Restaurant.objects.all()

        for i in restaurants:
            print(i.name)
            try:
                lat = geocode(client=gmaps, address=i.address)[0]['geometry']['location']['lat']
                lng = geocode(client=gmaps, address=i.address)[0]['geometry']['location']['lng']

                coords = [str(lat), str(lng)]
                destination = ", ".join(coords)

                i.coordinates = destination
                i.save()
            except IndexError:
                print(i.id, i.name, i.address)
                pass

        self.stdout.write(self.style.SUCCESS('Successfully filled DB'))
