from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from .models import Plane, Gate, Runway, Airport
from dateutil import parser
from .helpers import check_size, arrive_at_intersection_at_same_minute, check_time_delta, send_warning
import json

TEAM_ID = "nSLIoq2eIYMNExLYNALS"  # actual ID: nSLIoq2eIYMNExLYNALS


def index(request):
    return render(request, 'index.html', {})


@csrf_exempt
def handle_passenger_count(request):
    body = json.loads(request.body)
    print(body)
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    if plane.maxPassengerCount < int(body["passenger_count"]):
        send_warning({
            "team_id": TEAM_ID,
            "error": "TOO_MANY_PASSENGERS",
            "obj_type": "PLANE",
            "id": plane.identifier
        })
    return HttpResponse()


def check_gate(plane, gate, body):
    if not check_size(plane.size, gate.size):
        send_warning({
            "team_id": TEAM_ID,
            "error": "TOO_SMALL_GATE",
            "obj_type": "PLANE",
            "id": plane.identifier
        })
    date = parser.parse(body["arrive_at_time"])
    plane.arrive_at_gate_time = date
    plane.save()
    if gate.plane_set.filter(Q(arrive_at_gate_time=date) | Q(arrive_at_runway_time=None)).count() > 1:
        for plane in gate.plane_set.filter(Q(arrive_at_gate_time=date) | Q(arrive_at_runway_time=None)).all():
            send_warning({
                "team_id": TEAM_ID,
                "error": "DUPLICATE_GATE",
                "obj_type": "PLANE",
                "id": plane.identifier
            })


@csrf_exempt
def handle_gate_publish(request):
    body = json.loads(request.body)
    print(body)
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    gate = Gate.objects.filter(identifier=body["gate"]).first()
    plane.gate = gate
    if "arrive_at_time" in body:
        check_gate(plane, gate, body)
    else:
        plane.arrive_at_gate_time = None
        plane.runway = None
    plane.save()
    return HttpResponse()


def check_runway(plane, runway, body):
    if not check_size(plane.size, runway.size):
        send_warning({
            "team_id": TEAM_ID,
            "error": "TOO_SMALL_RUNWAY",
            "obj_type": "PLANE",
            "id": plane.identifier
        })
    date = parser.parse(body["arrive_at_time"])
    plane.arrive_at_runway_time = date
    plane.save()
    yup_collide = False
    if runway.plane_set.count() > 1:
        for other_plane in runway.plane_set.all():
            if plane != other_plane and check_time_delta(plane.arrive_at_runway_time,
                                                         other_plane.arrive_at_runway_time, timedelta(minutes=1)):
                yup_collide = True
                print("HERE")
                send_warning({
                    "team_id": TEAM_ID,
                    "error": "DUPLICATE_RUNWAY",
                    "obj_type": "PLANE",
                    "id": other_plane.identifier
                })
    if yup_collide:
        print("HERE")
        send_warning({
            "team_id": TEAM_ID,
            "error": "DUPLICATE_RUNWAY",
            "obj_type": "PLANE",
            "id": plane.identifier
        })


@csrf_exempt
def handle_runway_publish(request):
    body = json.loads(request.body)
    print(body)
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    runway = Runway.objects.filter(identifier=body["runway"]).first()
    plane.runway = runway
    if "arrive_at_time" in body:
        check_runway(plane, runway, body)
    else:
        plane.arrive_at_runway_time = None
        plane.gate = None
        plane.heading = 0
        plane.speed = 0
        plane.take_off_airport = plane.land_airport
        plane.land_airport = None
        plane.take_off_time = None
        plane.landing_time = None
    plane.save()
    return HttpResponse()


def check_airport(plane):
    if plane.airline not in plane.land_airport.airlines.all():
        send_warning({
            "team_id": TEAM_ID,
            "error": "WRONG_AIRPORT",
            "obj_type": "PLANE",
            "id": plane.identifier
        })


def check_set1(plane, set1, warned_for_current_plane):
    if set1.count() > 0:
        if not warned_for_current_plane:
            warned_for_current_plane = True
            send_warning({
                "team_id": TEAM_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": plane.identifier
            })
        for collidy_plane in set1.all():
            send_warning({
                "team_id": TEAM_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": collidy_plane.identifier
            })


def check_set2(plane, set2, warned_for_current_plane):
    if set2.count() > 0:
        if not warned_for_current_plane:
            warned_for_current_plane = True
            send_warning({
                "team_id": TEAM_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": plane.identifier
            })
        for collidy_plane in set2.all():
            send_warning({
                "team_id": TEAM_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": collidy_plane.identifier
            })


def check_set3(plane, set3, warned_for_current_plane):
    if set3.count() > 0:
        for collidy_plane in set3.all():
            if arrive_at_intersection_at_same_minute(plane, collidy_plane):
                if not warned_for_current_plane:
                    warned_for_current_plane = True
                    send_warning({
                        "team_id": TEAM_ID,
                        "error": "COLLISION_IMMINENT",
                        "obj_type": "PLANE",
                        "id": plane.identifier
                    })
                send_warning({
                    "team_id": TEAM_ID,
                    "error": "COLLISION_IMMINENT",
                    "obj_type": "PLANE",
                    "id": collidy_plane.identifier
                })


@csrf_exempt
def handle_heading_publish(request):
    body = json.loads(request.body)
    print(body)
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    direction = float(body["direction"])
    speed = float(body["speed"])
    origin = Airport.objects.filter(name=body["origin"]).first()
    destination = Airport.objects.filter(name=body["destination"]).first()
    take_off_time = parser.parse(body["take_off_time"])
    landing_time = parser.parse(body["landing_time"])

    plane.take_off_airport = origin
    plane.land_airport = destination
    plane.take_off_time = take_off_time
    plane.landing_time = landing_time
    plane.heading = direction
    plane.speed = speed
    plane.runway = None
    plane.save()

    check_airport(plane)

    warned_for_current_plane = False
    set1 = Plane.objects.exclude(landing_time=None).filter(take_off_airport=plane.land_airport,
                                                           land_airport=plane.take_off_airport)
    check_set1(plane, set1, warned_for_current_plane)

    set2 = Plane.objects.exclude(landing_time=None).filter(take_off_airport=plane.take_off_airport,
                                                           land_airport=plane.land_airport,
                                                           landing_time__gt=plane.landing_time)
    check_set2(plane, set2, warned_for_current_plane)

    # now check for intersecting planes
    set3 = Plane.objects.exclude(Q(take_off_airport=plane.take_off_airport, land_airport=plane.land_airport) | Q(
        take_off_airport=plane.land_airport, land_airport=plane.take_off_airport)).exclude(landing_time=None)
    check_set3(plane, set3, warned_for_current_plane)

    return HttpResponse()
