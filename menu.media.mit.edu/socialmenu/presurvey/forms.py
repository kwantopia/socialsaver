from django.forms import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from models import LegalsPopulationSurvey, TasteChoice

class LegalsPopulationSurveyForm(ModelForm):

    class Meta:
        model = LegalsPopulationSurvey
        choices = []
        for t in TasteChoice.objects.all():
            choices.append((t.id, t.sense))
        widgets = {
            'tastes': CheckboxSelectMultiple(choices=choices)
        }
