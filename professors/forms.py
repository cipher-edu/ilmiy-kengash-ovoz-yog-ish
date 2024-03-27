from django import forms
from .models import *

class UserAdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = UserCreate
        fields = ['name', 'lastname', 'surname', 'kaf', 'ilimiy_darajasi', 'user_lavozimi', 'tel', 'image', 'mail']
class VoteForm(forms.Form):
    unvon = forms.ModelChoiceField(queryset=IlmiyUnvon.objects.all(), empty_label=None, label='Select an object for voting')
    scientific_title = forms.ChoiceField(choices=(('yes', 'Yes'), ('no', 'No')), label='Scientific Title')
