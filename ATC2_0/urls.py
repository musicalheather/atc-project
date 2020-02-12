from django.contrib.auth.decorators import login_required, permission_required
from django.urls import path

from . import plane_views as plane
from . import runway_views as runway
from . import gate_views as gate
from . import airline_views as airline
from . import airport_views as airport
from . import views as overview

urlpatterns = [
    path('', login_required(overview.index), name='overview_index'),
    path('airport', permission_required("ATC2_0.view_airport")(login_required(airport.AirportList.as_view())), name='airport_index'),
    path('airport/new', permission_required("ATC2_0.add_airport")(login_required(airport.AirportCreate.as_view())), name='airport_create'),
    path('airport/<int:pk>/edit', permission_required("ATC2_0.change_airport")(login_required(airport.AirportUpdate.as_view())), name='airport_edit'),
    path('airport/<int:pk>/delete', permission_required("ATC2_0.delete_airport")(login_required(airport.AirportDelete.as_view())), name='airport_delete'),
    path('airline', permission_required("ATC2_0.view_airline")(login_required(airline.AirlineList.as_view())), name='airline_index'),
    path('airline/new', permission_required("ATC2_0.add_airline")(login_required(airline.AirlineCreate.as_view())), name='airline_create'),
    path('airline/<int:pk>/edit', permission_required("ATC2_0.change_airline")(login_required(airline.AirlineUpdate.as_view())), name='airline_edit'),
    path('airline/<int:pk>/delete', permission_required("ATC2_0.delete_airline")(login_required(airline.AirlineDelete.as_view())), name='airline_delete'),
    path('gate', permission_required("ATC2_0.view_gate")(login_required(gate.GateList.as_view())), name='gate_index'),
    path('gate/new', permission_required("ATC2_0.add_gate")(login_required(gate.GateCreate.as_view())), name='gate_create'),
    path('gate/<int:pk>/edit', permission_required("ATC2_0.change_gate")(login_required(gate.GateUpdate.as_view())), name='gate_edit'),
    path('gate/<int:pk>/delete', permission_required("ATC2_0.delete_gate")(login_required(gate.GateDelete.as_view())), name='gate_delete'),
    path('runway', permission_required("ATC2_0.view_runway")(login_required(runway.RunwayList.as_view())), name='runway_index'),
    path('runway/new', permission_required("ATC2_0.add_runway")(login_required(runway.RunwayCreate.as_view())), name='runway_create'),
    path('runway/<int:pk>/edit', permission_required("ATC2_0.change_runway")(login_required(runway.RunwayUpdate.as_view())), name='runway_edit'),
    path('runway/<int:pk>/delete', permission_required("ATC2_0.delete_runway")(login_required(runway.RunwayDelete.as_view())), name='runway_delete'),
    path('plane', permission_required("ATC2_0.view_plane")(login_required(plane.PlaneList.as_view())), name='plane_index'),
    path('plane/new', permission_required("ATC2_0.add_plane")(login_required(plane.PlaneCreate.as_view())), name='plane_create'),
    path('plane/<int:pk>/edit', permission_required("ATC2_0.change_plane")(login_required(plane.PlaneUpdate.as_view())), name='plane_edit'),
    path('plane/<int:pk>/delete', permission_required("ATC2_0.delete_plane")(login_required(plane.PlaneDelete.as_view())), name='plane_delete'),
    path('api/counts', overview.handle_passenger_count, name='passenger_count'),
    path('api/headings', overview.handle_heading_publish, name='handle_heading_publish'),
    path('api/gates', overview.handle_gate_publish, name='handle_gate_publish'),
    path('api/runways', overview.handle_runway_publish, name='handle_runway_publish'),
]
