from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from django.forms import ModelForm, ModelChoiceField
from django.urls import reverse_lazy
from .models import Plane, Airline, Gate, Runway

FIELDS = ["identifier", "size", "airline", "gate", "runway", "maxPassengerCount", "currentPassengerCount"]


class PlaneForm(ModelForm):
    class Meta:
        model = Plane
        fields = FIELDS

    def process_perms(self, request):
        if request is not None and not request.user.has_perm("perms.ATC2_0.add_airline"):
            del self.fields["identifier"]
            del self.fields["size"]
            del self.fields["airline"]
            del self.fields["gate"]
            del self.fields["runway"]
            del self.fields["maxPassengerCount"]

    airline = ModelChoiceField(required=True, queryset=Airline.objects.all())
    gate = ModelChoiceField(required=False, queryset=Gate.objects.all())
    runway = ModelChoiceField(required=False, queryset=Runway.objects.all())


class PlaneList(ListView):
    queryset = Plane.objects.order_by("identifier")
    template_name = "plane/index.html"


class PlaneCreate(CreateView):
    model = Plane
    form_class = PlaneForm
    template_name = "create_edit.html"
    success_url = reverse_lazy("plane_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class PlaneUpdate(UpdateView):
    model = Plane
    form_class = PlaneForm
    template_name = 'create_edit.html'
    success_url = reverse_lazy("plane_index")

    def get_form(self, ):
        form = super(PlaneUpdate, self).get_form()
        form.process_perms(self.request)
        return form

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class PlaneDelete(DeleteView):
    model = Plane
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy("plane_index")
