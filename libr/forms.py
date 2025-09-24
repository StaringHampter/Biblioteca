from django.forms import ModelForm, ModelChoiceField, Select
from .models import Estudiante

class PresetGrados(ModelForm):

	class Meta:
		model = Estudiante
		fields = ['grado', 'seccion']
