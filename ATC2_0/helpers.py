import requests

from .models import Plane, Airport
from math import sqrt, degrees, atan2
from datetime import timedelta


def send_warning(data):
    print(data)
    requests.post(url='https://evently.bjucps.dev/app/error_report', json=data)


def check_time_delta(first, second, max):
    if first is None or second is None:
        return False

    first = first.replace(tzinfo=None)
    second = second.replace(tzinfo=None)

    if first < second:
        return second - first < max
    else:
        return first - second < max


def calc_distance(origin_airport: Airport, dest_airport: Airport):
    return sqrt((dest_airport.x - origin_airport.x) ** 2 + (dest_airport.y - origin_airport.y) ** 2)


def calc_heading(origin_airport: Airport, dest_airport: Airport):
    theta = degrees(atan2(origin_airport.x - dest_airport.x, dest_airport.y - origin_airport.y));
    return (theta + 90) % 360


def check_size(plane_size: str, thing_size: str):
    if plane_size == "MEDIUM" and thing_size == "SMALL":
        return False
    if plane_size == "LARGE" and thing_size in ["SMALL", "MEDIUM"]:
        return False
    return True


def get_intersection_point(plane1: Plane, plane2: Plane):
    x1 = plane1.take_off_airport.x
    x2 = plane1.land_airport.x
    x3 = plane2.take_off_airport.x
    x4 = plane2.land_airport.x
    y1 = plane1.take_off_airport.y
    y2 = plane1.land_airport.y
    y3 = plane2.take_off_airport.y
    y4 = plane2.land_airport.y
    return (((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / (
            (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)),
            ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / (
                    (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)))


def calc_distance_with_tuple(origin_airport: Airport, dest: tuple):
    return sqrt((dest[0] - origin_airport.x) ** 2 + (dest[1] - origin_airport.y) ** 2)


def arrive_at_intersection_at_same_minute(plane1: Plane, plane2: Plane):
    try:
        intersection_point = get_intersection_point(plane1, plane2)
        p1dist = calc_distance_with_tuple(plane1.take_off_airport, intersection_point)
        p2dist = calc_distance_with_tuple(plane2.take_off_airport, intersection_point)
        p1arrive = plane1.take_off_time + timedelta(hours=p1dist / plane1.speed)
        p2arrive = plane2.take_off_time + timedelta(hours=p2dist / plane2.speed)
        return p1arrive.year == p2arrive.year and p1arrive.month == p2arrive.month and p1arrive.day == p2arrive.day \
               and p1arrive.hour == p2arrive.hour and p1arrive.minute == p2arrive.minute
    except:
        return False
