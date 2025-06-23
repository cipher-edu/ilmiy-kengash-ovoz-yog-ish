# apps/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Kafedra

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label="Ism")
    last_name = forms.CharField(max_length=100, required=True, label="Familiya")
    
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'surname', 'kafedra', 'academic_degree', 'position', 'phone_number', 'image']
        labels = {
            'surname': "Otasining ismi", 'kafedra': "Kafedrasi",
            'academic_degree': "Ilmiy darajasi", 'position': "Lavozimi",
            'phone_number': "Telefon raqami", 'image': "Profil rasmi",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['kafedra'].queryset = Kafedra.objects.all()

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            profile.save()
        return profile