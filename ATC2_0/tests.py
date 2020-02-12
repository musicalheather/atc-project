from django.test import Client, TestCase
from ATC2_0.models import Airline, Airport, Gate, Runway, Plane
from django.contrib.auth.models import User
from unittest.mock import patch
from datetime import datetime, timedelta
from .helpers import calc_heading, calc_distance
from django.core import management
import json

TEMPORARY = 'temporary'
EMAIL = 'temporary@gmail.com'
AIRPORT_END = '/atc/airport'
AIRLINE_END = '/atc/airline'
PLANE_END = '/atc/plane'
GATE_END = '/atc/gate'
RUNWAY_END = '/atc/runway'

TEST_AIRLINE = 'Delta 2'
TEST_AIRPORT = 'Test Airport'
TIME_FORMAT = "%Y-%m-%d %H:%M"


# less than 400 indicates success of some sort
class AirportTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username=TEMPORARY, email=EMAIL,
                                                  password=TEMPORARY)

    def test_airport_create_edit_delete(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        response = c.post(AIRPORT_END + '/new', {'name': 'ATL', 'x': '0.0', 'y': '0.0'})
        self.assertLess(response.status_code, 400)
        airport = Airport.objects.get(name='ATL')
        self.assertIsNotNone(airport)
        self.assertEqual(airport.x, 0.0)
        self.assertEqual(airport.y, 0.0)

        response = c.post(AIRPORT_END + f'/{airport.id}/edit', {'name': 'ATL', 'x': '1.0', 'y': '1.0'})
        self.assertLess(response.status_code, 400)
        airport = Airport.objects.get(name='ATL')
        self.assertEqual(airport.x, 1.0)
        self.assertEqual(airport.y, 1.0)

        response = c.post(AIRPORT_END + f'/{airport.id}/delete')
        try:
            airport = Airport.objects.get(name='ATL')
            self.assertTrue(True, False)  # we should not have gotten here
        except Airport.DoesNotExist:
            pass

        # cleanup
        Airport.objects.all().delete()

    def test_airport_create_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # airport with same name creation
        Airport.objects.create(name='ATL', x=0.0, y=0.0)
        response = c.post(AIRPORT_END + '/new', {'name': 'ATL', 'x': '0.0', 'y': '0.0'})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Airport.objects.all().delete()

    def test_airport_update_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # airport with same name during update
        airport1 = Airport.objects.create(name='ATL', x=0.0, y=0.0)
        Airport.objects.create(name='ATL2', x=0.0, y=0.0)
        response = c.post(AIRPORT_END + f'/{airport1.id}/edit', {'name': 'ATL2', 'x': '0.0', 'y': '0.0'})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Airport.objects.all().delete()

    def test_airport_delete_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # delete non existent airport
        response = c.get(AIRPORT_END + f'/1/delete')
        # should fail
        self.assertGreaterEqual(response.status_code, 400)


class AirlineTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username=TEMPORARY, email=EMAIL,
                                                  password=TEMPORARY)

    def test_airline_create_edit_delete(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # dependencies: Airport
        response = c.post(AIRPORT_END + '/new', {'name': 'Airline Test Airport', 'x': 1.0, 'y': 1.0})
        self.assertLess(response.status_code, 400)
        airport = Airport.objects.get(name='Airline Test Airport')

        response = c.post(AIRLINE_END + '/new', {'name': 'Delta', 'airports': [airport.id]})
        self.assertLess(response.status_code, 400)
        airline = Airline.objects.get(name='Delta')
        self.assertIsNotNone(airline)
        self.assertEqual(airline.airport_set.count(), 1)

        response = c.post(AIRLINE_END + f'/{airline.id}/edit', {'name': 'TEST_AIRLINE', 'airports': [airport.id]})
        self.assertLess(response.status_code, 400)
        try:
            airline = Airline.objects.get(name='Delta')
            self.assertTrue(True, False)  # we should not have gotten here
        except Airline.DoesNotExist:
            pass
        airline = Airline.objects.get(name='TEST_AIRLINE')
        self.assertIsNotNone(airline)
        self.assertEqual(airline.airport_set.count(), 1)

        response = c.post(AIRLINE_END + f'/{airline.id}/delete')
        self.assertLess(response.status_code, 400)
        try:
            airline = Airline.objects.get(name='TEST_AIRLINE')
            self.assertTrue(True, False)  # we should not have gotten here
        except Airline.DoesNotExist:
            pass

        # cleanup
        Airline.objects.all().delete()
        Airport.objects.all().delete()

    def test_airline_create_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # airline with same name creation
        Airline.objects.create(name='Delta')
        response = c.post(AIRLINE_END + '/new', {'name': 'Delta'})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Airline.objects.all().delete()

    def test_airline_update_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # airline with same name during update
        airline1 = Airline.objects.create(name='Delta')
        Airline.objects.create(name='Delta2')
        response = c.post(AIRLINE_END + f'/{airline1.id}/edit', {'name': 'Delta2'})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Airline.objects.all().delete()

    def test_airline_delete_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # delete non existent airline
        response = c.get(AIRLINE_END + '/1/delete')
        # should fail
        self.assertGreaterEqual(response.status_code, 400)


class GateTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username=TEMPORARY, email=EMAIL,
                                                  password=TEMPORARY)

    def test_gate_create_edit_delete(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # dependencies: Airport
        response = c.post(AIRPORT_END + '/new', {'name': TEST_AIRPORT, 'x': '0.0', 'y': '0.0'})
        self.assertLess(response.status_code, 400)
        airport = Airport.objects.get(name=TEST_AIRPORT)

        response = c.post(GATE_END + '/new', {'identifier': 'G1', 'size': 'SMALL', 'airport': airport.id})
        self.assertLess(response.status_code, 400)
        gate = Gate.objects.get(identifier='G1')
        self.assertIsNotNone(gate)
        self.assertEqual(gate.size, 'SMALL')
        self.assertEqual(gate.airport, airport)

        response = c.post(GATE_END + f'/{gate.id}/edit', {'identifier': 'G1', 'size': 'MEDIUM', 'airport': airport.id})
        self.assertLess(response.status_code, 400)
        gate = Gate.objects.get(identifier='G1')
        self.assertIsNotNone(gate)
        self.assertEqual(gate.size, 'MEDIUM')
        self.assertEqual(gate.airport, airport)

        response = c.get(GATE_END + f'/{gate.id}/delete')
        self.assertLess(response.status_code, 400)
        try:
            gate = Gate.objects.get(identifier='G1')
            self.assertTrue(True, False)  # we should not have gotten here
        except Gate.DoesNotExist:
            pass

        # cleanup
        Gate.objects.all().delete()
        Airport.objects.all().delete()

    def test_gate_create_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # gate with same name creation
        airport = Airport.objects.create(name=TEST_AIRPORT, x=0.0, y=0.0)
        Gate.objects.create(identifier='G1', size='SMALL', airport=airport)
        response = c.post(GATE_END + '/new', {'identifier': 'G1', 'size': 'SMALL', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)
        # gate with invalid size
        response = c.post(GATE_END + '/new', {'identifier': 'G2', 'size': 'TANGO', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Gate.objects.all().delete()
        Airport.objects.all().delete()

    def test_gate_update_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # gate with same name during update
        airport = Airport.objects.create(name=TEST_AIRPORT, x=0.0, y=0.0)
        gate1 = Gate.objects.create(identifier='G1', size='SMALL', airport=airport)
        Gate.objects.create(identifier='G2', size='SMALL', airport=airport)
        response = c.post(GATE_END + f'/{gate1.id}/edit', {'identifier': 'G2', 'size': 'SMALL', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # gate with invalid size
        response = c.post(GATE_END + f'/{gate1.id}/edit', {'identifier': 'G1', 'size': 'TANGO', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Gate.objects.all().delete()
        Airport.objects.all().delete()

    def test_gate_delete_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # delete non existent gate
        response = c.get(f'/gate/1/delete')
        # should fail
        self.assertGreaterEqual(response.status_code, 400)


class RunwayTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username=TEMPORARY, email=EMAIL,
                                                  password=TEMPORARY)

    def test_runway_create_edit_delete(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # dependencies: Airport
        response = c.post(AIRPORT_END + '/new', {'name': TEST_AIRPORT, 'x': '0.0', 'y': '0.0'})
        self.assertLess(response.status_code, 400)
        airport = Airport.objects.get(name=TEST_AIRPORT)

        response = c.post(RUNWAY_END + '/new', {'identifier': 'R1', 'size': 'SMALL', 'airport': airport.id})
        self.assertLess(response.status_code, 400)
        runway = Runway.objects.get(identifier='R1')
        self.assertIsNotNone(runway)
        self.assertEqual(runway.size, 'SMALL')
        self.assertEqual(runway.airport, airport)

        response = c.post(RUNWAY_END + f'/{runway.id}/edit',
                          {'identifier': 'R1', 'size': 'MEDIUM', 'airport': airport.id})
        self.assertLess(response.status_code, 400)
        runway = Runway.objects.get(identifier='R1')
        self.assertIsNotNone(runway)
        self.assertEqual(runway.size, 'MEDIUM')
        self.assertEqual(runway.airport, airport)

        response = c.get(RUNWAY_END + f'/{runway.id}/delete')
        self.assertLess(response.status_code, 400)
        try:
            runway = Runway.objects.get(identifier='R1')
            self.assertTrue(True, False)  # we should not have gotten here
        except Gate.DoesNotExist:
            pass

        # cleanup
        Runway.objects.all().delete()
        Runway.objects.all().delete()

    def test_runway_create_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # runway with same name creation
        airport = Airport.objects.create(name=TEST_AIRPORT, x=0.0, y=0.0)
        Runway.objects.create(identifier='R1', size='SMALL', airport=airport)
        response = c.post(RUNWAY_END + '/new', {'identifier': 'R1', 'size': 'SMALL', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)
        # gate with invalid size
        response = c.post(RUNWAY_END + '/new', {'identifier': 'R2', 'size': 'TANGO', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Runway.objects.all().delete()
        Airport.objects.all().delete()

    def test_runway_update_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # runway with same name during update
        airport = Airport.objects.create(name=TEST_AIRPORT, x=0.0, y=0.0)
        runway1 = Runway.objects.create(identifier='R1', size='SMALL', airport=airport)
        Runway.objects.create(identifier='R2', size='SMALL', airport=airport)
        response = c.post(RUNWAY_END + f'/{runway1.id}/edit',
                          {'identifier': 'R2', 'size': 'SMALL', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # gate with invalid size
        response = c.post(RUNWAY_END + f'/{runway1.id}/edit',
                          {'identifier': 'R1', 'size': 'TANGO', 'airport': airport.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Runway.objects.all().delete()
        Airport.objects.all().delete()

    def test_runway_delete_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # delete non existent runway
        response = c.get(RUNWAY_END + f'/1/delete')
        # should fail
        self.assertGreaterEqual(response.status_code, 400)


class PlaneTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username=TEMPORARY, email=EMAIL,
                                                  password=TEMPORARY)

    def test_plane_create_edit_delete(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # dependencies: Airline, Gate, Runway
        airport = Airport.objects.create(name=TEST_AIRPORT, x=0.0, y=0.0)
        response = c.post(AIRLINE_END + '/new', {'name': TEST_AIRLINE, 'airports': [airport.id]})
        self.assertLess(response.status_code, 400)
        airline = Airline.objects.get(name=TEST_AIRLINE)
        response = c.post(GATE_END + '/new', {'identifier': 'G1', 'size': 'SMALL', 'airport': airport.id})
        self.assertLess(response.status_code, 400)
        gate = Gate.objects.get(identifier='G1')
        response = c.post(RUNWAY_END + '/new', {'identifier': 'R1', 'size': 'SMALL', 'airport': airport.id})
        self.assertLess(response.status_code, 400)
        runway = Runway.objects.get(identifier='R1')

        response = c.post(PLANE_END + '/new',
                          {'identifier': 'P1', 'size': 'SMALL', 'currentPassengerCount': 20, 'maxPassengerCount': 250,
                           'airline': airline.id, 'gate': gate.id, 'runway': runway.id})
        self.assertLess(response.status_code, 400)
        plane = Plane.objects.get(identifier='P1')
        self.assertIsNotNone(plane)
        self.assertEqual(plane.size, 'SMALL')
        self.assertEqual(plane.currentPassengerCount, 20)
        self.assertEqual(plane.maxPassengerCount, 250)
        self.assertEqual(plane.airline, airline)
        self.assertEqual(plane.gate, gate)
        self.assertEqual(plane.runway, runway)

        response = c.post(PLANE_END + f'/{plane.id}/edit',
                          {'identifier': 'P2', 'size': 'SMALL', 'currentPassengerCount': 20, 'maxPassengerCount': 250,
                           'airline': airline.id, 'gate': gate.id, 'runway': runway.id})
        self.assertLess(response.status_code, 400)
        plane = Plane.objects.get(identifier='P2')
        self.assertIsNotNone(plane)
        self.assertEqual(plane.size, 'SMALL')
        self.assertEqual(plane.currentPassengerCount, 20)
        self.assertEqual(plane.maxPassengerCount, 250)
        self.assertEqual(plane.airline, airline)
        self.assertEqual(plane.gate, gate)
        self.assertEqual(plane.runway, runway)

        response = c.post(PLANE_END + f'/{plane.id}/delete')
        self.assertLess(response.status_code, 400)
        try:
            plane = Plane.objects.get(identifier='P1')
            self.assertTrue(True, False)  # we should not have gotten here
        except Plane.DoesNotExist:
            pass

        # cleanup
        Gate.objects.all().delete()
        Runway.objects.all().delete()
        Airline.objects.all().delete()
        Plane.objects.all().delete()
        Airport.objects.all().delete()

    def test_plane_create_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # runway with same name creation
        airline = Airline.objects.create(name=TEST_AIRLINE)
        Plane.objects.create(identifier='P1', size='SMALL', currentPassengerCount=20, maxPassengerCount=250,
                             airline=airline)
        response = c.post(PLANE_END + '/new',
                          {'identifier': 'P1', 'size': 'SMALL', 'currentPassengerCount': 20, 'maxPassengerCount': 250,
                           'airline': airline.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)
        # gate with invalid size
        response = c.post(PLANE_END + '/new',
                          {'identifier': 'P2', 'size': 'TANGO', 'currentPassengerCount': 20, 'maxPassengerCount': 250,
                           'airline': airline.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Plane.objects.all().delete()
        Airport.objects.all().delete()

    def test_plane_update_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # plane with same name during update
        airline = Airline.objects.create(name=TEST_AIRLINE)
        plane1 = Plane.objects.create(identifier='P1', size='SMALL', currentPassengerCount=20, maxPassengerCount=250,
                                      airline=airline)
        Plane.objects.create(identifier='P2', size='SMALL', currentPassengerCount=20, maxPassengerCount=250,
                             airline=airline)
        response = c.post(RUNWAY_END + f'/{plane1.id}/edit',
                          {'identifier': 'P2', 'size': 'SMALL', 'currentPassengerCount': 20, 'maxPassengerCount': 250,
                           'airline': airline.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # gate with invalid size
        response = c.post(RUNWAY_END + f'/{plane1.id}/edit',
                          {'identifier': 'P1', 'size': 'TANGO', 'currentPassengerCount': 20, 'maxPassengerCount': 250,
                           'airline': airline.id})
        # should fail
        self.assertGreaterEqual(response.status_code, 400)

        # cleanup
        Plane.objects.all().delete()
        Airport.objects.all().delete()

    def test_plane_delete_validation(self):
        c = Client()
        logged_in = c.login(username=TEMPORARY, password=TEMPORARY)
        self.assertEqual(logged_in, True)
        # delete non existent plane
        response = c.get(PLANE_END + f'/1/delete')
        # should fail
        self.assertGreaterEqual(response.status_code, 400)


@patch("ATC2_0.views.send_warning", autospec=True)
class SimulationTests(TestCase):
    headings_url = '/atc/api/headings'
    runways_url = '/atc/api/runways'
    gates_url = '/atc/api/gates'
    counts_url = '/atc/api/counts'
    content_type = "application/json"
    def setUp(self):
        management.call_command("load_data")
        management.call_command("load_data")  # should do nothing

    def test_head_on_collision(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="gnfasudtlm").first()
        plane2 = Plane.objects.filter(identifier="matxovlzow").first()
        airport1 = Airport.objects.filter(name="kkz").first()
        airport2 = Airport.objects.filter(name="xhz").first()
        take_off = datetime.now()
        landing = datetime.now() + timedelta(hours=1)

        c.post(self.headings_url, data=json.dumps({
            "plane": plane1.identifier,
            "direction": calc_heading(airport1, airport2),
            "speed": calc_distance(airport1, airport2),
            "origin": airport1.name,
            "destination": airport2.name,
            "take_off_time": take_off.strftime(TIME_FORMAT),
            "landing_time": landing.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        c.post(self.headings_url, data=json.dumps({
            "plane": plane2.identifier,
            "direction": calc_heading(airport2, airport1),
            "speed": calc_distance(airport2, airport1),
            "origin": airport2.name,
            "destination": airport1.name,
            "take_off_time": take_off.strftime(TIME_FORMAT),
            "landing_time": landing.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)

    def test_rear_collision(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="gnfasudtlm").first()
        plane2 = Plane.objects.filter(identifier="matxovlzow").first()
        airport1 = Airport.objects.filter(name="kkz").first()
        airport2 = Airport.objects.filter(name="xhz").first()
        take_off = datetime.now()
        landing1 = datetime.now() + timedelta(hours=1)

        c.post(self.headings_url, data=json.dumps({
            "plane": plane1.identifier,
            "direction": calc_heading(airport1, airport2),
            "speed": calc_distance(airport1, airport2) / 2.5,
            "origin": airport1.name,
            "destination": airport2.name,
            "take_off_time": (take_off - timedelta(hours=1)).strftime(TIME_FORMAT),
            "landing_time": (landing1 + timedelta(minutes=30)).strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        c.post(self.headings_url, data=json.dumps({
            "plane": plane2.identifier,
            "direction": calc_heading(airport1, airport2),
            "speed": calc_distance(airport1, airport2),
            "origin": airport1.name,
            "destination": airport2.name,
            "take_off_time": take_off.strftime(TIME_FORMAT),
            "landing_time": landing1.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)

    def test_tbone_collision(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="gnfasudtlm").first()
        plane2 = Plane.objects.filter(identifier="matxovlzow").first()
        airport1 = Airport.objects.filter(name="oap").first()
        airport2 = Airport.objects.filter(name="kkz").first()
        airport3 = Airport.objects.filter(name="mfz").first()
        take_off = datetime.now()
        landing = datetime.now() + timedelta(hours=1)

        c.post(self.headings_url, data=json.dumps({
            "plane": plane1.identifier,
            "direction": calc_heading(airport1, airport3),
            "speed": calc_distance(airport1, airport3),
            "origin": airport1.name,
            "destination": airport3.name,
            "take_off_time": take_off.strftime(TIME_FORMAT),
            "landing_time": landing.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        c.post(self.headings_url, data=json.dumps({
            "plane": plane2.identifier,
            "direction": calc_heading(airport2, airport3),
            "speed": calc_distance(airport2, airport3),
            "origin": airport2.name,
            "destination": airport3.name,
            "take_off_time": take_off.strftime(TIME_FORMAT),
            "landing_time": landing.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)

    def test_duplicate_gate(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="mopyahgbal").first()
        plane2 = Plane.objects.filter(identifier="rzmwdhqblw").first()
        gate = Gate.objects.filter(identifier="jemhnkkldw").first()
        arrival = datetime.now() + timedelta(hours=1)

        c.post(self.gates_url, data=json.dumps({
            "plane": plane1.identifier,
            "gate": gate.identifier,
            "arrive_at_time": arrival.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        c.post(self.gates_url, data=json.dumps({
            "plane": plane2.identifier,
            "gate": gate.identifier,
            "arrive_at_time": arrival.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)

    def test_duplicate_runway(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="mopyahgbal").first()
        plane2 = Plane.objects.filter(identifier="rzmwdhqblw").first()
        runway = Runway.objects.filter(identifier="qkegovbsbo").first()
        arrival = datetime.now() + timedelta(hours=1)

        c.post(self.runways_url, data=json.dumps({
            "plane": plane1.identifier,
            "runway": runway.identifier,
            "arrive_at_time": arrival.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        c.post(self.runways_url, data=json.dumps({
            "plane": plane2.identifier,
            "runway": runway.identifier,
            "arrive_at_time": arrival.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)

    def test_too_small_gate(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="khnndacsrj").first()
        gate = Gate.objects.filter(identifier="poyktqlblw").first()
        arrival = datetime.now() + timedelta(hours=1)

        c.post(self.gates_url, data=json.dumps({
            "plane": plane1.identifier,
            "gate": gate.identifier,
            "arrive_at_time": arrival.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)

    def test_too_small_runway(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="khnndacsrj").first()
        runway = Runway.objects.filter(identifier="iagriywrss").first()
        arrival = datetime.now() + timedelta(hours=1)

        c.post(self.runways_url, data=json.dumps({
            "plane": plane1.identifier,
            "runway": runway.identifier,
            "arrive_at_time": arrival.strftime(TIME_FORMAT)
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)

    def test_too_many_passengers(self, mock_call_external_api):
        c = Client()
        self.assertEqual(mock_call_external_api.called, False)
        plane1 = Plane.objects.filter(identifier="khnndacsrj").first()

        c.post(self.counts_url, data=json.dumps({
            "plane": plane1.identifier,
            "passenger_count": 500
        }), content_type=self.content_type)
        self.assertEqual(mock_call_external_api.called, True)
