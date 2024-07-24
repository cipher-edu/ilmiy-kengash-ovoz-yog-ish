from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin, User
from django.db.models import Count
from collections import Counter
# Create your models here.
fakultets = [
        ("Umumiy pedagogika va psixologiya","Umumiy pedagogika va psixologiya"),
        ("Maktabgacha ta’lim", "Maktabgacha ta’lim"),
        ("Boshlang‘ich ta’lim", "Boshlang‘ich ta’lim"),
        ("Pedagogika va psixologiya", "Pedagogika va psixologiya"),
        ("Musiqa ta’limi", "Musiqa ta’limi"),
        ("Tasviriy san’at va muhandislik grafikasi", "Tasviriy san’at va muhandislik grafikasi"),
        ("Biologiya", "Biologiya"),
        ("Kimyo", "Kimyo"),
        ("Geografiya va iqtisodiy bilim asoslari", "Geografiya va iqtisodiy bilim asoslari"),
        ("Matematika", "Matematika"),
        ("Informatika", "Informatika"),
        ("Fizika va astronomiya", "Fizika va astronomiya"),
        ("Texnologik ta’lim", "Texnologik ta’lim"),
        ("O‘zbek tilshunosligi", "O‘zbek tilshunosligi"),
        ("O‘zbek tili va adabiyoti", "O‘zbek tili va adabiyoti"),
        ("Tarix", "Tarix"),
        ("Milliy g‘oya, ma’naviyat asoslari va huquq ta’limi", "Milliy g‘oya, ma’naviyat asoslari va huquq ta’limi"),
        ("Ijtimoiy fanlar", "Ijtimoiy fanlar"),
        ("Jismoni madaniyat", "Jismoni madaniyat"),
        ("Sport turlarini o‘qitish metodikasi", "Sport turlarini o‘qitish metodikasi"),
        ("Ingliz tili va adabiyoti", "Ingliz tili va adabiyoti"),
        ("Ingliz tili amaliy kursi", "Ingliz tili amaliy kursi"),
        ("Fakultetlararo chet tillar", "Fakultetlararo chet tillar"),
        ("Rus tili va adabiyoti", "Rus tili va adabiyoti"),
        ("Qozoq tili va adabiyoti", "Qozoq tili va adabiyoti"),
        ("Umumiy tibbiy fanlar", "Umumiy tibbiy fanlar"),
    ]


class UserCreate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User,on_delete=models.CASCADE )
    name = models.CharField(max_length=25, verbose_name='Ismi')
    lastname = models.CharField(max_length=25, verbose_name='Familiyasi')
    surname = models.CharField(max_length=25, verbose_name='Otasining ismi')
    kaf = models.CharField(max_length=155, choices=fakultets, default=None, verbose_name='Kafedrasi')
    ilimiy_darajasi = models.CharField(max_length=255,  verbose_name='Ma\'lumoti')
    user_lavozimi = models.CharField(max_length=255, verbose_name='Lavozimi')
    tel = models.IntegerField(verbose_name='Telefon raqami')
    image = models.ImageField(upload_to='user_logo/')
    mail = models.CharField(max_length=250, verbose_name='Mail')
    
    
    @classmethod
    def total_professor(cls):
        return cls.objects.count()
    
    def __str__(self):
        return self.lastname

tanlov = (
    ('Xa', 'Xa'), ('yoq', 'Yoq'), ('betaraf', 'Betaraf'),
)

tanlovcha = (
    ('kafedra mudiri', 'kafedra mudiri'), 
    ('kafedra professori', 'kafedra professori'), 
    ('kafedra dotsenti', 'kafedra dotsenti'), 
    ("kafedra katta o‘qituvchisi","kafedra katta o‘qituvchisi"), 
    ("kafedra o‘qituvchisi lavozimi","kafedra o‘qituvchisi lavozimi")
)

# IlmiyUnvon modeli
class IlmiyUnvon(models.Model):
    name = models.CharField(max_length=255, verbose_name='Ism Familiya sharif')
    unvon = models.CharField(max_length=255, verbose_name='Ilmiy Unvon')
    unvon_shifr = models.CharField(max_length=255, verbose_name='Ilmiy Unvon Shifri')
    kaf = models.CharField(max_length=155, choices=fakultets, default=None, verbose_name='Kafedrasi')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ilmiy Unvon"
        verbose_name_plural = "Ilmiy Unvonlar"

# Tanlov modeli
class Tanlov(models.Model):
    name = models.CharField(max_length=255, verbose_name='Ism Familiya sharif')
    kaf = models.CharField(max_length=155, choices=fakultets, default=None, verbose_name='Kafedrasi')
    scientific_title = models.CharField(max_length=255, choices=tanlovcha, verbose_name="Lavozimni tanlang")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tanlov"
        verbose_name_plural = "Tanlovlar"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tanlov = models.ForeignKey(Tanlov, on_delete=models.CASCADE)
    
    ovoz = models.CharField(max_length=10, choices=[('Xa', 'Xa'), ('yoq', 'Yoq'), ('betaraf', 'Betaraf')], verbose_name='Ovoz')

    def __str__(self):
        return f"{self.tanlov.name} - {self.ovoz}"

    class Meta:
        verbose_name = "Ovoz Berish"
        verbose_name_plural = "Ovoz Berishlar"

class Vote2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ilmiy = models.ForeignKey(IlmiyUnvon, on_delete=models.CASCADE)
    ovoz = models.CharField(max_length=10, choices=[('Xa', 'Xa'), ('yoq', 'Yoq'), ('betaraf', 'Betaraf')], verbose_name='Ovoz')

    def __str__(self):
        return f"{self.ilmiy.name} - {self.ovoz}"

    class Meta:
        verbose_name = "Ovoz Berish"
        verbose_name_plural = "Ovoz Berishlar"


    # unvon = models.ForeignKey(IlmiyUnvon, on_delete=models.CASCADE, verbose_name='Saylanuvchi')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Foydalanuvchi ismi')
    # scientific_title = models.CharField(
    #     max_length=20,
    #     choices=tanlov,
    #     default='betaraf',
    #     verbose_name="O'z ovozingini tanlang"
    # )

    # class Meta:
    #     verbose_name = "Ovoz berish"
    #     verbose_name_plural = "Ovoz berish"

    # @staticmethod
    # def count_votes():
    #     votes = Vote.objects.all()
    #     scientific_titles = [vote.scientific_title for vote in votes]
    #     vote_counts = Counter(scientific_titles)
    #     return dict(vote_counts)

