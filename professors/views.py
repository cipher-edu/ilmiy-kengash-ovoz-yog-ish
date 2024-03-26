from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import CreateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserAdditionalInfoForm
from .models import *

# Create your views here.
class SingUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def form_valid(self, form):
        # Automatically set the user as staff upon registration
        user = form.save(commit=False)
        user.is_staff = True
        user.save()
        return super().form_valid(form)


@login_required
def user_info_form(request):
    try:
        user_create_instance = request.user.usercreate
    except UserCreate.DoesNotExist:
        user_create_instance = None

    if request.method == 'POST':
        form = UserAdditionalInfoForm(request.POST, request.FILES, instance=user_create_instance)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.user = request.user
            form_instance.save()
            return redirect('home')  # Redirect to the desired page after saving
    else:
        form = UserAdditionalInfoForm(instance=user_create_instance)

    return render(request, 'registration/user_info_form.html', {'form': form})
