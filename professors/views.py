from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DetailView, View
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .forms import *
from .models import IlmiyUnvon, Vote, Tanlov
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
def error_view(request):
    return render(request, 'error.html')

def success_view(request):
    return render(request, 'success.html')

@login_required
def tanlov_list(request):
    unvons = Tanlov.objects.all()
    voted_unvons = Vote.objects.filter(user=request.user).values_list('tanlov_id', flat=True)
    return render(request, 'vote_list.html', {'unvons': unvons, 'voted_unvons': voted_unvons})


@csrf_exempt
@login_required
def vote(request):
    if request.method == 'POST':
        user = request.user
        vote_data = {}

        # Collect vote data
        for unvon_id in request.POST.getlist('unvon_ids'):
            vote_value = request.POST.get(f'vote_{unvon_id}')
            if vote_value:
                vote_data[unvon_id] = vote_value

        # Save votes
        for unvon_id, vote_value in vote_data.items():
            try:
                tanlov = Tanlov.objects.get(id=unvon_id)
                Vote.objects.update_or_create(
                    user=user,
                    tanlov=tanlov,
                    defaults={'ovoz': vote_value}
                )
            except Tanlov.DoesNotExist:
                continue

        # Render the updated list of votes
        unvons = Tanlov.objects.all()
        voted_unvons = Vote.objects.filter(user=request.user).values_list('tanlov_id', flat=True)
        html = render_to_string('vote_list.html', {'unvons': unvons, 'voted_unvons': voted_unvons})
        return JsonResponse({'status': 'success', 'message': 'Ovoz muvaffaqiyatli saqlandi.'})

    return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri so\'rov turi.'})




@login_required
def tanlov_list2(request):
    ilmiy_unvons = IlmiyUnvon.objects.all()
    voted_unvons = Vote2.objects.filter(user=request.user).values_list('ilmiy_id', flat=True)
    return render(request, 'vote_list2.html', {'ilmiy_unvons': ilmiy_unvons, 'voted_unvons': voted_unvons})

@csrf_exempt
@login_required
def vote2(request):
    if request.method == 'POST':
        user = request.user
        vote_data = {}

        # Collect vote data
        for unvon_id in request.POST.getlist('unvon_ids'):
            vote_value = request.POST.get(f'vote_{unvon_id}')
            if vote_value:
                vote_data[unvon_id] = vote_value

        # Debugging output
        print(f"Received vote data: {vote_data}")

        # Save votes
        for unvon_id, vote_value in vote_data.items():
            try:
                ilmiy_unvon = IlmiyUnvon.objects.get(id=unvon_id)
                # Check if the vote already exists
                vote, created = Vote2.objects.update_or_create(
                    user=user,
                    ilmiy=ilmiy_unvon,
                    defaults={'ovoz': vote_value}
                )
                if created:
                    print(f"Vote created: {vote}")
                else:
                    print(f"Vote updated: {vote}")
            except IlmiyUnvon.DoesNotExist:
                print(f"IlmiyUnvon with id {unvon_id} does not exist.")
                continue

        return JsonResponse({'status': 'success', 'message': 'Ovoz muvaffaqiyatli saqlandi.'})

    return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri so\'rov turi.'})




#statstic
def vote_counts(request):
    ilmiy_votes = []
    for ilmiy in IlmiyUnvon.objects.all():
        votes = {
            'kengash': ilmiy.kengash.name,  # Include kengash name
            'name': ilmiy.name,
            'Xa': Vote2.objects.filter(ilmiy=ilmiy, ovoz='Xa').count(),
            'Yoq': Vote2.objects.filter(ilmiy=ilmiy, ovoz='yoq').count(),
            'Betaraf': Vote2.objects.filter(ilmiy=ilmiy, ovoz='betaraf').count(),
        }
        ilmiy_votes.append(votes)
    
    tanlov_votes = []
    for tanlov in Tanlov.objects.all():
        votes = {
            'name': tanlov.name,
            'Xa': Vote.objects.filter(tanlov=tanlov, ovoz='Xa').count(),
            'Yoq': Vote.objects.filter(tanlov=tanlov, ovoz='yoq').count(),
            'Betaraf': Vote.objects.filter(tanlov=tanlov, ovoz='betaraf').count(),
        }
        tanlov_votes.append(votes)
    
    context = {
        'ilmiy_votes': ilmiy_votes,
        'tanlov_votes': tanlov_votes,
    }
    
    return render(request, 'vote_results.html', context)


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
