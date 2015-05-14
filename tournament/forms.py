from django import forms
from .models import Team


class TeamEditForm(forms.ModelForm):

	class Meta:
		model = Team
		fields = ('name', 'slug', 'leader', 'entry_code')