from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('vote/create/', VoteCreateView.as_view(), name='vote_create'),
    path('vote/<int:pk>/update/', VoteUpdateView.as_view(), name='vote_update'),
    path('vote/<int:pk>/', VoteDetailView.as_view(), name='vote_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SingUpView.as_view(), name='signup'),
    path('user-info/', user_info_form, name='user_info'),
    path('stat/', VoteStatisticsView.as_view(), name='stat'),
    path('list/', tanlov_list, name='tanlov_list'),
    path('vote/', vote, name='vote'),  # Ensure this is the correct path
    path('list2/', tanlov_list2, name='tanlov_list2'),
    path('vote2/', vote2, name='vote2'), 
    path('success/', vote_success, name='vote_success'),
    path('results/', vote_results, name='vote_results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
