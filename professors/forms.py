from django import forms
from .models import UserCreate

class UserAdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = UserCreate
        fields = ['name', 'lastname', 'surname', 'kaf', 'ilimiy_darajasi', 'user_lavozimi', 'tel', 'image', 'mail']
