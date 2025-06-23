# apps/apps.py

from django.apps import AppConfig

class ProfessorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'professors' # "professors" o'rniga o'zingizning app nomingizni yozing

    def ready(self):
        # Signal'larni import qilish
        import professors.signals 