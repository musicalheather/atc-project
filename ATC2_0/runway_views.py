from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from django.forms import ModelForm, ModelChoiceField
from django.urls import reverse_lazy
from .models import Runway, Airport

FIELDS = ["identifier", "size", "airport"]


class RunwayForm(ModelForm):
    class Meta:
        model = Runway
        fields = FIELDS

    airport = ModelChoiceField(required=True, queryset=Airport.objects.all())


class RunwayList(ListView):
    queryset = Runway.objects.order_by("identifier")
    template_name = "runway/index.html"


class RunwayCreate(CreateView):
    model = Runway
    form_class = RunwayForm
    template_name = "create_edit.html"
    success_url = reverse_lazy("runway_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class RunwayUpdate(UpdateView):
    model = Runway
    form_class = RunwayForm
    template_name = 'create_edit.html'
    success_url = reverse_lazy("runway_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class RunwayDelete(DeleteView):
    model = Runway
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy("runway_index")
