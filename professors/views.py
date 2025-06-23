# professors/views.py

import json
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import Count, Q

from .models import (
    Byulleten, Vote, Saylov, Tanlov, SaylovVote, IlmiyUnvon,
    BoshqaMasala, Kengash, User, UserProfile
)
from .forms import CustomUserCreationForm, UserProfileForm

# ==============================================================================
# FOYDALANUVCHILARNI BOSHQARISH
# ==============================================================================
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'registration/profile_form.html'
    success_url = reverse_lazy('home')
    def get_object(self, queryset=None): return self.request.user.profile

# ==============================================================================
# OVOZ BERISH JARAYONI
# ==============================================================================
class ByulletenListView(LoginRequiredMixin, ListView):
    model = Byulleten
    template_name = 'voting/byulleten_list.html'
    context_object_name = 'byulletenlar'
    def get_queryset(self):
        return Byulleten.objects.filter(is_active=True).select_related('kengash')

# professors/views.py

class ByulletenDetailView(LoginRequiredMixin, DetailView):
    model = Byulleten
    template_name = 'voting/byulleten_detail.html'
    context_object_name = 'byulleten'

    def get_queryset(self):
        """
        Byulletenga bog'liq barcha ma'lumotlarni bitta so'rovda oldindan yuklaymiz.
        Bu yerda 'saylovlar__nomzodlar' muhim.
        """
        return Byulleten.objects.prefetch_related(
            'saylovlar__nomzodlar__saylov__lavozim',  # To'liq zanjirni prefetch qilamiz
            'unvonlar',
            'boshqa_masalalar'
        ).filter(is_active=True)

    def get_context_data(self, **kwargs):
        """Shablonga kerakli barcha context o'zgaruvchilarini yuboramiz."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Ovoz berilganlikni tekshirish uchun ma'lumotlar
        context['voted_items'] = set(Vote.objects.filter(user=user).values_list('content_type_id', 'object_id'))
        context['voted_saylov_ids'] = set(SaylovVote.objects.filter(user=user).values_list('saylov_id', flat=True))
        
        # Content Type'lar
        context['content_types'] = {
            'ilmiyunvon': ContentType.objects.get_for_model(IlmiyUnvon).id,
            'boshqamasala': ContentType.objects.get_for_model(BoshqaMasala).id,
        }
        
        # Shablonning o'zida ".all" qilish o'rniga, shu yerda o'zgaruvchilarga olamiz
        byulleten = self.get_object()
        context['saylovlar_list'] = byulleten.saylovlar.all()
        context['unvonlar_list'] = byulleten.unvonlar.all()
        context['boshqa_masalalar_list'] = byulleten.boshqa_masalalar.all()
        
        return context

@login_required
def submit_votes(request):
    """AJAX orqali barcha turdagi ovozlarni qabul qiladi."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Faqat POST so\'rovlariga ruxsat etilgan.'}, status=405)
    try:
        user = request.user
        # 1. Saylov ovozlarini qayta ishlash
        for key, candidate_id in request.POST.items():
            if key.startswith('saylov_'):
                saylov_id = key.split('_')[1]
                SaylovVote.objects.update_or_create(
                    user=user, saylov_id=saylov_id,
                    defaults={'chosen_candidate_id': candidate_id}
                )

        # 2. Standart ovozlarni qayta ishlash
        for key, ovoz_value in request.POST.items():
            if key.startswith('vote_'):
                parts = key.split('_')
                if len(parts) == 3:
                    content_type_id = int(parts[1])
                    object_id = int(parts[2])
                    Vote.objects.update_or_create(
                        user=user, content_type_id=content_type_id, object_id=object_id,
                        defaults={'ovoz': ovoz_value}
                    )
        return JsonResponse({'status': 'success', 'message': 'Ovozlaringiz muvaffaqiyatli qabul qilindi!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Serverda kutilmagan xatolik: {e}'}, status=500)

# ==============================================================================
# NATIJALARNI KO'rish
# ==============================================================================
class BallotResultsListView(LoginRequiredMixin, ListView):
    model = Byulleten
    template_name = 'results/results_list.html'
    context_object_name = 'byulletenlar'

    def get_queryset(self):
        voted_ballot_ids = set()
        # Saylov ovozlari orqali byulleten id'larni olish
        voted_ballot_ids.update(SaylovVote.objects.values_list('saylov__byulletenlar__id', flat=True))
        # Standart ovozlar orqali byulleten id'larni olish (GenericForeignKey uchun to'g'ri ishlash)
        for unvon in IlmiyUnvon.objects.filter(votes__isnull=False).distinct():
            voted_ballot_ids.update(unvon.byulletenlar.values_list('id', flat=True))
        for masala in BoshqaMasala.objects.filter(votes__isnull=False).distinct():
            voted_ballot_ids.update(masala.byulletenlar.values_list('id', flat=True))
        return Byulleten.objects.filter(id__in=voted_ballot_ids).select_related('kengash').distinct()

# professors/views.py

class BallotResultsDetailView(LoginRequiredMixin, DetailView):
    model = Byulleten
    template_name = 'results/results_detail.html'
    context_object_name = 'byulleten'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        byulleten = self.get_object()
        vote_choices = Vote.OvozChoices

        # --- JADVAL MA'LUMOTLARI ---
        
        # 1. Saylov natijalari
        saylov_results = []
        # Diagramma uchun ma'lumotlarni yig'ish
        saylov_charts_data = []

        for saylov in byulleten.saylovlar.all():
            nomzodlar_data = []
            chart_series = []
            chart_labels = []
            
            for nomzod in saylov.nomzodlar.all():
                ha_count = SaylovVote.objects.filter(chosen_candidate=nomzod).count()
                nomzodlar_data.append({'nomzod': nomzod, 'ha_count': ha_count})
                chart_series.append(ha_count)
                chart_labels.append(nomzod.candidate_name)

            total_votes = SaylovVote.objects.filter(saylov=saylov).count()
            
            # Agar ovozlar bo'lsa, "Qarshilar" va "Betaraflar" yo'qligi sababli
            # bu saylovda ishtirok etmaganlar sonini hisoblashimiz mumkin.
            # Lekin bu mantiqni murakkablashtiradi. Hozircha faqat "Ha" ovozlarini ko'rsatamiz.
            
            saylov_results.append({'saylov': saylov, 'nomzodlar': nomzodlar_data, 'total_votes': total_votes})
            saylov_charts_data.append({
                'id': saylov.id,
                'title': saylov.title,
                'series': chart_series,
                'labels': chart_labels
            })
        context['saylov_results'] = saylov_results
        
        # 2. Standart natijalar
        def get_annotated_queryset(model):
            return model.objects.filter(byulletenlar=byulleten).annotate(
                ha_count=Count('votes', filter=Q(votes__ovoz=vote_choices.HA)),
                yoq_count=Count('votes', filter=Q(votes__ovoz=vote_choices.YOQ)),
                betaraf_count=Count('votes', filter=Q(votes__ovoz=vote_choices.BETARAF))
            ).filter(Q(ha_count__gt=0) | Q(yoq_count__gt=0) | Q(betaraf_count__gt=0))

        context['title_votes'] = get_annotated_queryset(IlmiyUnvon)
        context['other_issue_votes'] = get_annotated_queryset(BoshqaMasala)
        
        # --- DIAGRAMMA MA'LUMOTLARI (JSON) ---
        context['saylov_charts_data'] = json.dumps(saylov_charts_data)
        
        return context

# ==============================================================================
# BOSH SAHIFA
# ==============================================================================
@login_required
def home(request):
    """Bosh sahifa uchun view."""
    context = {
        'total_votes': Vote.objects.count() + SaylovVote.objects.count(),
        'council_count': Kengash.objects.count(),
        'user_count': User.objects.filter(is_active=True).count(),
        'active_ballots': Byulleten.objects.filter(is_active=True).count(),
    }
    return render(request, 'index.html', context)