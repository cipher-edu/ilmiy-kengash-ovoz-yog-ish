# professors/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # ==================================
    # Asosiy va Boshqaruv sahifalari
    # ==================================
    path('', views.home, name='home'),
    
    # ==================================
    # Autentifikatsiya va Profil
    # ==================================
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.UserProfileUpdateView.as_view(), name='profile_update'),

    # ==================================
    # Ovoz Berish Jarayoni
    # ==================================
    # Barcha aktiv byulletenlar ro'yxati (ovoz berish uchun)
    path('ballots/', views.ByulletenListView.as_view(), name='byulleten_list'),
    
    # Bitta byulleten uchun ovoz berish sahifasi
    path('ballots/<int:pk>/', views.ByulletenDetailView.as_view(), name='byulleten_detail'),

    # Ovozlarni yuborish uchun yagona AJAX endpoint
    path('vote/submit/', views.submit_votes, name='submit_votes'), 
    
    # ==================================
    # Natijalarni ko'rish
    # ==================================
    # Barcha byulletenlar ro'yxatini ko'rsatuvchi sahifa (natijalarni tanlash uchun)
    path('results/', views.BallotResultsListView.as_view(), name='results_list'),
    
    # Tanlangan byulletenning natijalarini ko'rsatuvchi sahifa
    path('results/<int:pk>/', views.BallotResultsDetailView.as_view(), name='results_detail'),
]