import csv

from django.contrib.auth.models import User

from ATC2_0.models import Airport, Airline, Gate, Runway, Plane
from django.core.management.base import BaseCommand


def load_airports():
    loaded = False
    if Airport.objects.count() == 0:
        loaded = True
        with open("datasets/airport.csv") as file:
            reader = csv.DictReader(file)
            for airport in reader:
                Airport.objects.create(
                    name=airport["name"],
                    x=float(airport["x"]),
                    y=float(airport["y"])
                )
        print("airports loaded")
    else:
        print("airports already loaded")
    return loaded


def load_airlines():
    loaded = False
    if Airline.objects.count() == 0:
        loaded = True
        with open("datasets/airline.csv") as file:
            reader = csv.DictReader(file)
            for airline in reader:
                Airline.objects.create(name=airline["name"])
        print("airlines loaded")
    else:
        print("airlines already loaded")
    return loaded


def load_gates():
    if Gate.objects.count() == 0:
        with open("datasets/gate.csv") as file:
            reader = csv.DictReader(file)
            for gate in reader:
                Gate.objects.create(
                    identifier=gate["id"],
                    airport=Airport.objects.get(name=gate["airport"]),
                    size=gate["size"]
                )
        print("gates loaded")
    else:
        print("gates already loaded")


def load_runways():
    if Runway.objects.count() == 0:
        with open("datasets/runway.csv") as file:
            reader = csv.DictReader(file)
            for runway in reader:
                Runway.objects.create(
                    identifier=runway["id"],
                    airport=Airport.objects.get(name=runway["airport"]),
                    size=runway["size"]
                )
        print("runways loaded")
    else:
        print("runways already loaded")


def load_planes():
    if Plane.objects.count() == 0:
        with open("datasets/plane.csv") as file:
            reader = csv.DictReader(file)
            for plane in reader:
                Plane.objects.create(
                    identifier=plane["id"],
                    airline=Airline.objects.get(name=plane["airline"]),
                    size=plane["size"],
                    currentPassengerCount=0,
                    maxPassengerCount=plane["maxPassenger"]
                )
        print("planes loaded")
    else:
        print("planes already loaded")


def load_users():
    if User.objects.count() == 0:
        User.objects.create_superuser(username='joanna', password='jojo', email='')
        User.objects.create_superuser(username='phil', password='popo', email='')
        User.objects.create_superuser(username='heather', password='hehe', email='')
        User.objects.create_superuser(username='hudson', password='huhu', email='')
        User.objects.create_superuser(username='carlos', password='lolo', email='')
        User.objects.create_superuser(username='doctor', password='docdocgo', email='')
        print("users loaded")
    else:
        print("users already loaded")


class Command(BaseCommand):
    help = 'loads data into database if needed'

    def handle(self, *args, **options):
        loaded_airports = load_airports()
        loaded_airlines = load_airlines()

        if loaded_airports or loaded_airlines:
            with open("datasets/airport_airline.csv") as file:
                reader = csv.DictReader(file)
                for combo in reader:
                    Airport.objects.get(
                        name=combo["airport"]
                    ).airlines.add(
                        Airline.objects.get(name=combo["airline"])
                    )
            print("airport / airlines loaded")
        else:
            print("airport / airlines already loaded")

        load_gates()
        load_runways()
        load_planes()
        load_users()
