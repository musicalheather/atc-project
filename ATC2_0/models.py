from django.db import models
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError
from django_prometheus.models import ExportModelOperationsMixin

SIZES = [
    ('SMALL', 'Small'),
    ('MEDIUM', 'Medium'),
    ('LARGE', 'Large')
]


def is_size_valid(my_size: str, assigned_size: str) -> bool:
    if my_size == 'SMALL':
        return True
    if my_size == 'MEDIUM' and assigned_size not in ['MEDIUM', 'LARGE']:
        return False
    if my_size == 'LARGE' and assigned_size != 'LARGE':
        return False
    return True


class Airline(ExportModelOperationsMixin('airline'), models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airport(ExportModelOperationsMixin('airport'), models.Model):
    name = models.CharField(max_length=255, unique=True)
    x = models.FloatField()
    y = models.FloatField()
    airlines = models.ManyToManyField(Airline)

    def clean(self):
        if Airport.objects.filter(x=self.x, y=self.y).count() != 0:
            raise ValidationError("airports cannot be co-located")

    def __str__(self):
        return self.name


class Gate(ExportModelOperationsMixin('gate'), models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    size = models.CharField(max_length=6, choices=SIZES, default='SMALL')
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    def __str__(self):
        return self.identifier


class Runway(ExportModelOperationsMixin('runawy'), models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    size = models.CharField(max_length=6, choices=SIZES, default='SMALL')
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    def __str__(self):
        return self.identifier


class Plane(ExportModelOperationsMixin('plane'), models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    size = models.CharField(max_length=6, choices=SIZES, default='SMALL')
    currentPassengerCount = models.IntegerField()
    maxPassengerCount = models.IntegerField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    gate = models.ForeignKey(Gate, on_delete=models.SET_NULL, blank=True, null=True)
    runway = models.ForeignKey(Runway, on_delete=models.SET_NULL, blank=True, null=True)
    take_off_airport = models.ForeignKey(Airport, related_name="take_off_airport", on_delete=models.SET_NULL, null=True)
    land_airport = models.ForeignKey(Airport, related_name="landing_airport", on_delete=models.SET_NULL, null=True)
    heading = models.FloatField(null=True)
    speed = models.FloatField(null=True)
    take_off_time = models.DateTimeField(null=True)
    landing_time = models.DateTimeField(null=True)
    arrive_at_gate_time = models.DateTimeField(null=True)
    arrive_at_runway_time = models.DateTimeField(null=True)

    def clean(self):
        if self.gate is not None and not is_size_valid(self.size, self.gate.size):
            raise ValidationError("gate size must be equal or large to plane size")
        if self.runway is not None and not is_size_valid(self.size, self.runway.size):
            raise ValidationError("gate size must be equal or large to plane size")
        if self.currentPassengerCount > self.maxPassengerCount:
            raise ValidationError("currentPassengerCount cannot be greater than maxPassengerCount")

    def __str__(self):
        return self.identifier
