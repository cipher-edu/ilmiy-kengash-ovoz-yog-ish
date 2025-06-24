# professors/views.py

import json
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Q, Exists, OuterRef
from django.utils import timezone

from .models import (
    Byulleten, Vote, Saylov, Tanlov, SaylovVote, IlmiyUnvon,
    BoshqaMasala, Kengash, User, UserProfile
)
from .forms import CustomUserCreationForm, UserProfileForm

# ==============================================================================
# FOYDALANUVCHILARNI BOSHQARISH
# ==============================================================================
class SignUpView(CreateView):
    """Foydalanuvchilarni ro'yxatdan o'tkazish uchun view."""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Foydalanuvchi profilini tahrirlash uchun view."""
    form_class = UserProfileForm
    template_name = 'registration/profile_form.html'
    success_url = reverse_lazy('home')
    def get_object(self, queryset=None): return self.request.user.profile

# ============================================================================== 
# OVOZ BERISH JARAYONI (TUZATILGAN RUXSATLAR BILAN)
# ==============================================================================
from django.views.generic import ListView
from django.utils import timezone
from django.db.models import Case, When, BooleanField
class ByulletenListView(LoginRequiredMixin, ListView):
    """Faol, muddati o'tmagan va ruxsat etilgan byulletenlar ro'yxati (sahifalash bilan)."""
    model = Byulleten
    template_name = 'voting/byulleten_list.html'
    context_object_name = 'byulletenlar'
    paginate_by = 10  # Har bir sahifada 10 tadan byulleten

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        
        # Superuser barcha aktiv byulletenlarni ko'radi
        if user.is_superuser:
            base_queryset = Byulleten.objects.filter(is_active=True)
        else:
            # Oddiy foydalanuvchi faqat o'ziga ruxsat etilgan byulletenlarni ko'radi
            base_queryset = Byulleten.objects.filter(
                is_active=True,
                allowed_users=user
            )

        # Byulletenning muddati o'tgan yoki o'tmaganligini aniqlash uchun `annotate` ishlatamiz
        # Bu shablonda if/else qilishdan ko'ra samaraliroq
        queryset = base_queryset.annotate(
            is_expired=Case(
                When(end_time__isnull=False, end_time__lt=now, then=True),
                default=False,
                output_field=BooleanField()
            ),
            is_not_started=Case(
                When(start_time__isnull=False, start_time__gt=now, then=True),
                default=False,
                output_field=BooleanField()
            )
        ).select_related('kengash').order_by('is_expired', 'is_not_started', '-created_at')
        # SARALASH:
        # 1. Avval muddati o'tmaganlari (is_expired=False)
        # 2. Keyin hali boshlanmaganlari (is_not_started=False)
        # 3. Va oxirida eng yangilari (-created_at) birinchi bo'lib keladi
        
        return queryset.distinct()

# professors/views.py

# ... boshqa importlar va view'lar ...

# professors/views.py

# ... boshqa importlar va view'lar ...

class ByulletenDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Bitta byulleten uchun ovoz berish sahifasi (ruxsat va vaqt tekshiruvi bilan)."""
    model = Byulleten
    template_name = 'voting/byulleten_detail.html'
    context_object_name = 'byulleten'

    def get_queryset(self):
        # Bu metod o'zgarishsiz qoladi
        return Byulleten.objects.prefetch_related(
            'saylovlar__nomzodlar', 'unvonlar', 'boshqa_masalalar'
        ).filter(is_active=True)

    def test_func(self):
        # Bu metod o'zgarishsiz qoladi
        byulleten = self.get_object()
        user = self.request.user
        now = timezone.now()
        
        is_allowed = user.is_superuser or byulleten.allowed_users.filter(id=user.id).exists()
        if not is_allowed: return False
        if byulleten.start_time and byulleten.start_time > now: return False
        if byulleten.end_time and byulleten.end_time < now: return False
            
        return True
    
    def handle_no_permission(self):
        # Bu metod o'zgarishsiz qoladi
        return HttpResponseForbidden("Sizga ushbu sahifani ko'rishga ruxsat berilmagan yoki ovoz berish muddati mos emas.")

    def get_context_data(self, **kwargs):
        """Shablonga 'all_voted' statusini qo'shib yuboramiz."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        byulleten = self.get_object()
        
        # --- YANGI MANTIQ BOSHLANISHI ---

        # 1. Byulletendagi jami masalalar sonini hisoblaymiz
        saylov_count = byulleten.saylovlar.count()
        unvon_count = byulleten.unvonlar.count()
        boshqa_masala_count = byulleten.boshqa_masalalar.count()
        total_issues_count = saylov_count + unvon_count + boshqa_masala_count
        
        # 2. Foydalanuvchi ovoz bergan masalalar sonini hisoblaymiz
        voted_saylov_ids = set(SaylovVote.objects.filter(user=user, saylov__in=byulleten.saylovlar.all()).values_list('saylov_id', flat=True))
        
        # Standart ovozlar uchun ContentType'larni olamiz
        unvon_ct = ContentType.objects.get_for_model(IlmiyUnvon)
        boshqa_masala_ct = ContentType.objects.get_for_model(BoshqaMasala)
        
        voted_unvon_count = Vote.objects.filter(user=user, content_type=unvon_ct, object_id__in=byulleten.unvonlar.values('id')).count()
        voted_boshqa_masala_count = Vote.objects.filter(user=user, content_type=boshqa_masala_ct, object_id__in=byulleten.boshqa_masalalar.values('id')).count()
        
        total_voted_count = len(voted_saylov_ids) + voted_unvon_count + voted_boshqa_masala_count

        # 3. Solishtiramiz va natijani shablonga yuboramiz
        all_voted = False
        if total_issues_count > 0 and total_voted_count >= total_issues_count:
            all_voted = True
        
        context['all_voted'] = all_voted

        # --- YANGI MANTIQ TUGASHI ---

        # Shablon uchun boshqa kerakli ma'lumotlar
        context['voted_saylov_ids'] = voted_saylov_ids # Bu avvaldan bor edi, saqlab qolamiz
        context['voted_items'] = set(Vote.objects.filter(user=user).values_list('content_type_id', 'object_id'))
        context['content_types'] = {
            'ilmiyunvon': unvon_ct.id,
            'boshqamasala': boshqa_masala_ct.id,
        }
        
        return context
# ... qolgan barcha view'lar ...

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
                saylov_obj = Saylov.objects.get(id=saylov_id)
                byulleten = saylov_obj.byulletenlar.first()
                if byulleten and byulleten.end_time and byulleten.end_time < timezone.now():
                    continue 

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
# NATIJALARNI KO'RISH
# ==============================================================================
class BallotResultsListView(LoginRequiredMixin, ListView):
    model = Byulleten
    template_name = 'results/results_list.html'
    context_object_name = 'byulletenlar'

    def get_queryset(self):
        user = self.request.user

        voted_in_saylov = Saylov.objects.filter(byulletenlar=OuterRef('pk'), votes__isnull=False)
        voted_in_unvon = IlmiyUnvon.objects.filter(byulletenlar=OuterRef('pk'), votes__isnull=False)
        voted_in_masala = BoshqaMasala.objects.filter(byulletenlar=OuterRef('pk'), votes__isnull=False)

        queryset = Byulleten.objects.annotate(
            has_vote=Exists(voted_in_saylov) | Exists(voted_in_unvon) | Exists(voted_in_masala)
        ).filter(has_vote=True).select_related('kengash')

        if user.is_superuser:
            return queryset.distinct()
        
        return queryset.filter(allowed_users=user).distinct()

class BallotResultsDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Byulleten
    template_name = 'results/results_detail.html'
    context_object_name = 'byulleten'
    
    def test_func(self):
        byulleten = self.get_object()
        user = self.request.user
        return user.is_superuser or byulleten.allowed_users.filter(id=user.id).exists()

    def handle_no_permission(self):
        return HttpResponseForbidden("Sizga ushbu natijalarni ko'rishga ruxsat berilmagan.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        byulleten = self.get_object()
        vote_choices = Vote.OvozChoices

        # Saylov natijalari
        saylov_results = []
        saylov_charts_data = []
        for saylov in byulleten.saylovlar.all():
            nomzodlar_data, chart_series, chart_labels = [], [], []
            total_votes = SaylovVote.objects.filter(saylov=saylov).count()
            for nomzod in saylov.nomzodlar.all():
                ha_count = SaylovVote.objects.filter(chosen_candidate=nomzod).count()
                nomzodlar_data.append({'nomzod': nomzod, 'ha_count': ha_count})
                chart_series.append(ha_count)
                chart_labels.append(nomzod.candidate_name)
            
            saylov_results.append({'saylov': saylov, 'nomzodlar': nomzodlar_data, 'total_votes': total_votes})
            saylov_charts_data.append({'id': saylov.id, 'title': saylov.title, 'series': chart_series, 'labels': chart_labels})
        context['saylov_results'] = saylov_results
        
        # Standart natijalar
        def get_annotated_queryset(model):
            return model.objects.filter(byulletenlar=byulleten).annotate(
                ha_count=Count('votes', filter=Q(votes__ovoz=vote_choices.HA)),
                yoq_count=Count('votes', filter=Q(votes__ovoz=vote_choices.YOQ)),
                betaraf_count=Count('votes', filter=Q(votes__ovoz=vote_choices.BETARAF))
            ).filter(Q(ha_count__gt=0) | Q(yoq_count__gt=0) | Q(betaraf_count__gt=0))
        context['title_votes'] = get_annotated_queryset(IlmiyUnvon)
        context['other_issue_votes'] = get_annotated_queryset(BoshqaMasala)
        
        context['saylov_charts_data'] = json.dumps(saylov_charts_data)
        return context

# ==============================================================================
# BOSH SAHIFA
# ==============================================================================
@login_required
def home(request):
    """Bosh sahifa uchun view."""
    user = request.user
    active_ballots_count = 0
    if user.is_authenticated:
        now = timezone.now()
        active_ballots = Byulleten.objects.filter(is_active=True).filter(
            Q(start_time__isnull=True) | Q(start_time__lte=now)
        ).filter(
            Q(end_time__isnull=True) | Q(end_time__gte=now)
        )
        if user.is_superuser:
            active_ballots_count = active_ballots.count()
        else:
            active_ballots_count = active_ballots.filter(allowed_users=user).count()

    context = {
        'total_votes': Vote.objects.count() + SaylovVote.objects.count(),
        'council_count': Kengash.objects.count(),
        'user_count': User.objects.filter(is_active=True).count(),
        'active_ballots': active_ballots_count,
    }
    return render(request, 'index.html', context)