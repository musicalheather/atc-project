from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from django.forms import ModelForm, ModelChoiceField
from django.urls import reverse_lazy
from .models import Gate, Airport

FIELDS = ["identifier", "size", "airport"]


class GateForm(ModelForm):
    class Meta:
        model = Gate
        fields = FIELDS

    airport = ModelChoiceField(required=True, queryset=Airport.objects.all())


class GateList(ListView):
    queryset = Gate.objects.order_by("identifier")
    template_name = "gate/index.html"


class GateCreate(CreateView):
    model = Gate
    form_class = GateForm
    template_name = "create_edit.html"
    success_url = reverse_lazy("gate_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class GateUpdate(UpdateView):
    model = Gate
    form_class = GateForm
    template_name = 'create_edit.html'
    success_url = reverse_lazy("gate_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class GateDelete(DeleteView):
    model = Gate
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy("gate_index")
