from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SingUpView.as_view(), name='signup'),
    path('user-info/', user_info_form, name='user_info'),
    path('list/', tanlov_list, name='tanlov_list'),
    path('vote/', vote, name='vote'),  # Ensure this is the correct path
    path('list2/', tanlov_list2, name='tanlov_list2'),
    path('vote2/', vote2, name='vote2'), 
    path('results/', vote_counts, name='vote_results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
