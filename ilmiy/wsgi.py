<<<<<<< HEAD
"""
WSGI config for ilmiy project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

=======
>>>>>>> 453e8c51bdc84fdbd4bcf278f5016d15c1ba53f9
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ilmiy.settings')

application = get_wsgi_application()
