from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('', home, name='home'),
    path('vote/<uuid:unvon_id>/', vote, name='vote'),
  path('vote/success/', vote_success, name='vote_success'),
    path('vote/create/', VoteCreateView.as_view(), name='vote_create'),
    path('vote/<int:pk>/update/', VoteUpdateView.as_view(), name='vote_update'),
    path('vote/<int:pk>/', VoteDetailView.as_view(), name='vote_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/',PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complate'),
    path('signup/', SingUpView.as_view(), name='signup'),
    path('user-info/', user_info_form, name='user_info'),
    path('list/', vote_list, name='list'),
    path('natija/', vote_lists, name='natija')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
