from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from django.forms import ModelForm, ModelMultipleChoiceField
from django.urls import reverse_lazy
from .models import Airline, Airport

FIELDS = ["name", "airports"]


class AirlineForm(ModelForm):
    class Meta:
        model = Airline
        fields = FIELDS

    airports = ModelMultipleChoiceField(required=False, queryset=Airport.objects.all())

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['airports'] = [t.pk for t in kwargs['instance'].airport_set.all()]
        ModelForm.__init__(self, *args, **kwargs)

    # Overriding save allows us to process the value of 'toppings' field
    def save(self, commit=True):
        # Get the unsave Pizza instance
        instance = ModelForm.save(self, False)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # This is where we actually link the pizza with toppings
            instance.airport_set.clear()
            instance.airport_set.add(*self.cleaned_data['airports'])

        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance


class AirlineList(ListView):
    queryset = Airline.objects.order_by("name")
    template_name = "airline/index.html"


class AirlineCreate(CreateView):
    model = Airline
    form_class = AirlineForm
    template_name = "create_edit.html"
    success_url = reverse_lazy("airline_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class AirlineUpdate(UpdateView):
    model = Airline
    form_class = AirlineForm
    template_name = 'create_edit.html'
    success_url = reverse_lazy("airline_index")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class AirlineDelete(DeleteView):
    model = Airline
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy("airline_index")
