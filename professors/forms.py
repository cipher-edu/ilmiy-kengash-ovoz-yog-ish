from django import forms
from .models import *

class UserAdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = UserCreate
        fields = ['name', 'lastname', 'surname', 'kaf', 'ilimiy_darajasi', 'user_lavozimi', 'tel', 'image', 'mail']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}),
            'lastname': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}), 
            'surname': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}),
            'kaf': forms.Select(attrs={'class':'form-control col-md-6 mb-6'}),
            'ilimiy_darajasi': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}),
            'user_lavozimi': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}),
            'tel': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}),
            'image': forms.FileInput(attrs={'class':'form-control'}),
            'about': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}),
            'telegram': forms.TextInput(attrs={'class':'form-control col-md-12 mb-6'}),
            'mail': forms.TextInput(attrs={'class':'form-control col-md-6 mb-6'}),
        }

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['scientific_title']
        widgets = {
          'scientific_title'  : forms.Select(attrs={'class':'form-control'}),
        }