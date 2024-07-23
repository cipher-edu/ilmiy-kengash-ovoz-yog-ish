from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('vote/<uuid:unvon_id>/', vote, name='vote'),
    # path('vote/success/', vote_success, name='vote_success'),
    path('vote/create/', VoteCreateView.as_view(), name='vote_create'),
    path('vote/<int:pk>/update/', VoteUpdateView.as_view(), name='vote_update'),
    path('vote/<int:pk>/', VoteDetailView.as_view(), name='vote_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SingUpView.as_view(), name='signup'),
    path('user-info/', user_info_form, name='user_info'),
    path('list/', vote_list, name='list'),
    path('stat/', VoteStatisticsView.as_view(), name='stat'),
    path('list/', vote_list, name='vote_list'),
    path('success/', vote_success, name='vote_success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
