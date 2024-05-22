from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from .forms import UserAdditionalInfoForm, VoteForm
from .models import *
from django.views.generic import CreateView, UpdateView, DetailView, View


def handler404(request, exception):
    return render(request, '404.html', status=404)

@login_required
def vote(request, unvon_id):
    unvon = get_object_or_404(IlmiyUnvon, pk=unvon_id)
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            user = request.user
            scientific_title = form.cleaned_data['scientific_title']
            vote = Vote.objects.create(unvon=unvon, user=user, scientific_title=scientific_title)
            return redirect('vote_success')
    else:
        form = VoteForm()
    return render(request, 'vote.html', {'form': form})

def vote_success(request):
    return render(request, 'vote_success.html')


def vote_list(request):
    unvons = IlmiyUnvon.objects.all()
    user = request.user
    for unvon in unvons:
        unvon.voted_by_user = Vote.objects.filter(user=user, unvon=unvon).exists()
    return render(request, 'vote_list.html', {'unvons': unvons})


class VoteStatisticsView(View):
    def get(self, request):
        titles = IlmiyUnvon.objects.all()
        vote_counts = {}
        for title in titles:
            title_votes = Vote.objects.filter(unvon=title)
            vote_counts[title] = {
                'xa': title_votes.filter(scientific_title='Xa').count(),
                'yoq': title_votes.filter(scientific_title='yoq').count(),
                'betaraf': title_votes.filter(scientific_title='betaraf').count()
            }
        total_votes = Vote.objects.count()
        context = {
            'vote_counts': vote_counts,
            'total_votes': total_votes,
            'titles': titles
        }
        return render(request, 'vote_natija.html', context)



@login_required
def home(request):
    votes = Vote.objects.all()
    context = {
        'votes': votes
    }
    return render(request, 'index.html', context)

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
