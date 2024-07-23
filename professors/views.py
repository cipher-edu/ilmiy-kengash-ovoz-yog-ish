from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DetailView, View
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .forms import *
from .models import IlmiyUnvon, Vote, Tanlov

def error_view(request):
    return render(request, 'error.html')

def success_view(request):
    return render(request, 'success.html')
@login_required
def vote_list(request):
    if request.method == 'POST':
        tanlov_id = request.POST.get('tanlov_id')

        if not tanlov_id:
            return render(request, 'vote_list.html', {'error': 'Tanlov ID is missing'})

        try:
            tanlov = Tanlov.objects.get(id=tanlov_id)
        except Tanlov.DoesNotExist:
            return render(request, 'vote_list.html', {'error': 'Invalid Tanlov ID'})

        form = VoteForm(request.POST, tanlov=tanlov)
        if form.is_valid():
            try:
                form.save(user=request.user)
                return redirect('success')
            except Exception as e:
                return render(request, 'vote_list.html', {'form': form, 'error': str(e)})
        else:
            return render(request, 'vote_list.html', {'form': form})

    else:
        tanlov_id = request.GET.get('tanlov_id')

        if not tanlov_id:
            return render(request, 'vote_list.html', {'error': 'Tanlov ID is missing'})

        try:
            tanlov = Tanlov.objects.get(id=tanlov_id)
        except Tanlov.DoesNotExist:
            return render(request, 'vote_list.html', {'error': 'Invalid Tanlov ID'})

        unvons = IlmiyUnvon.objects.all()
        voted_unvons = Vote.objects.filter(user=request.user, tanlov=tanlov).values_list('ilmiy_unvon_id', flat=True)
        context = {
            'unvons': unvons,
            'voted_unvons': voted_unvons,
            'tanlov_id': tanlov_id,
            'form': VoteForm(tanlov=tanlov)
        }
        return render(request, 'vote_list.html', context)

@login_required
def vote_success(request):
    return render(request, 'vote_success.html')


@login_required
def vote(request, unvon_id):
    unvon = get_object_or_404(IlmiyUnvon, pk=unvon_id)
    
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            ovoz = form.cleaned_data['ovoz']
            # Check if the user has already voted for this unvon
            if not Vote.objects.filter(user=request.user, ilmiy_unvon=unvon).exists():
                Vote.objects.create(
                    ilmiy_unvon=unvon,
                    user=request.user,
                    ovoz=ovoz
                )
                return redirect('vote_success')
            else:
                # Handle the case where the user has already voted
                return render(request, 'vote.html', {'form': form, 'unvon': unvon, 'error': 'Siz allaqachon ovoz berdingiz.'})
    else:
        form = VoteForm()
    
    return render(request, 'vote.html', {'form': form, 'unvon': unvon})

class VoteStatisticsView(View):
    def get(self, request):
        titles = IlmiyUnvon.objects.all()
        vote_counts = {}
        for title in titles:
            title_votes = Vote.objects.filter(ilmiy_unvon=title)
            vote_counts[title] = {
                'xa': title_votes.filter(ovoz='Xa').count(),
                'yoq': title_votes.filter(ovoz='yoq').count(),
                'betaraf': title_votes.filter(ovoz='betaraf').count()
            }
        total_votes = Vote.objects.count()
        context = {
            'vote_counts': vote_counts,
            'total_votes': total_votes,
            'titles': titles
        }
        return render(request, 'vote_natija.html', context)

def vote_statistics(request):
    ilmiy_unvon_list = IlmiyUnvon.objects.all()
    vote_counts = {}
    total_votes = Vote.objects.count()
    selected_votes = Vote.objects.filter(ovoz__in=['Xa', 'yoq', 'betaraf']).count()
    
    for ilmiy_unvon in ilmiy_unvon_list:
        vote_counts[ilmiy_unvon] = ilmiy_unvon.count_votes_by_title()

    return render(request, 'vote_natija.html', {
        'vote_counts': vote_counts,
        'total_votes': total_votes,
        'selected_votes': selected_votes
    })

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
