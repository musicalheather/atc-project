from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from django.forms import ModelForm, ModelMultipleChoiceField
from django.urls import reverse_lazy
from .models import Airport, Airline

FIELDS = ["name", "x", "y", "airlines"]


class AirportForm(ModelForm):
    class Meta:
        model = Airport
        fields = FIELDS

    airlines = ModelMultipleChoiceField(required=False, queryset=Airline.objects.all())


class AirportList(ListView):
    queryset = Airport.objects.order_by("name")
    template_name = "airport/index.html"


class AirportCreate(CreateView):
    model = Airport
    form_class = AirportForm
    template_name = "create_edit.html"
    success_url = reverse_lazy("airport_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class AirportUpdate(UpdateView):
    model = Airport
    form_class = AirportForm
    template_name = 'create_edit.html'
    success_url = reverse_lazy("airport_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class AirportDelete(DeleteView):
    model = Airport
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy("airport_index")
