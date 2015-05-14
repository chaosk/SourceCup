from django import forms
from .models import Team


class TeamEditForm(forms.ModelForm):

	class Meta:
		model = Team
		fields = ('name', 'tag', 'leader', 'entry_code')


class TeamCreateForm(forms.ModelForm):

	class Meta:
		model = Team
		fields = ('name', 'tag')
		exclude = ('leader',)
