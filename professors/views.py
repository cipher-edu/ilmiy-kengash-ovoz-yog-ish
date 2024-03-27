from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import CreateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import UserAdditionalInfoForm
from .models import *
from django.views.generic import CreateView, UpdateView, DetailView
from .forms import VoteForm

@login_required
def vote(request):
    try:
        user_create_instance = UserCreate.objects.get(user=request.user)
    except UserCreate.DoesNotExist:
        user_create_instance = None

    objects_for_voting = IlmiyUnvon.objects.all()
    
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            unvon_id = form.cleaned_data['unvon']
            unvon_object = IlmiyUnvon.objects.get(pk=unvon_id)
            
            vote_instance, created = Vote.objects.get_or_create(user=user_create_instance, defaults={'unvon': unvon_object})
            if not created:
                # User has already voted
                return redirect('already_voted')

            return redirect('home')
    else:
        form = VoteForm()

    return render(request, 'vote.html', {'form': form, 'objects_for_voting': objects_for_voting})
class VoteCreateView(CreateView):
    model = Vote
    form_class = VoteForm
    template_name = 'vote_create.html'

class VoteUpdateView(UpdateView):
    model = Vote
    form_class = VoteForm
    template_name = 'vote_update.html'

class VoteDetailView(DetailView):
    model = Vote
    template_name = 'vote_detail.html'

@login_required
def home(request):
    vote = Vote.objects.all()
    context = {
        'vote':vote
    }
    return render(request, 'index.html', context)
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
