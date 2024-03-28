from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin, User
from django.db.models import Count
# Create your models here.
fakultets = [
        ('Metematika - Informatika', 'Matematika - Informatika'),
        ('Fizika', 'Fizika'),
        ('Sana\'tshunoslik','Sana\'tshunoslik'),
        ('Jismoniy madaniyat','Jismoniy madaniyat'),
        ('Tabiy fanlar', 'Tabiy fanlar'),
        ('Ingliz tili va adabiyoti','Ingliz tili va adabiyoti'),
        ('Rus tili va Qozoq tillari filialogiyasi', 'Rus tili va Qozoq tillari filialogiyasi'),
        ('Tibbiyot','Tibbiyot'),
        ('Maktabgacha va boshlang\'ich ta\'lim','Maktabgacha va boshlang\'ich ta\'lim'),
        ('Tarix', 'Tarix'),
        ('O‘zbek tili va adabiyoti fakulteti', 'O‘zbek tili va adabiyoti fakulteti'),

    ]

class UserCreate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User,on_delete=models.CASCADE )
    name = models.CharField(max_length=25, verbose_name='Ismi')
    lastname = models.CharField(max_length=25, verbose_name='Familiyasi')
    surname = models.CharField(max_length=25, verbose_name='Otasining ismi')
    kaf = models.CharField(max_length=155, choices=fakultets, default=None, verbose_name='Fakulteti')
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


class IlmiyUnvon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unvon = models.CharField(max_length=255, verbose_name='Ilmiy Unvon')
    name = models.CharField(max_length=255, verbose_name='Ism Familiya sharif')
    kaf = models.CharField(max_length=155, choices=fakultets, default=None, verbose_name='Fakulteti')
    voted_by_user = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return self.unvon
    
    class Meta:
        verbose_name = "Ilmiy Unvon"
        verbose_name_plural = "Ilmiy Unvonlar"

    def total_votes(self):
        return self.vote_set.count()

    def selected_votes(self):
        return self.vote_set.filter(scientific_title__in=['Xa', 'Yo\'q', 'Betaraf']).count()

    def count_votes_for_scientific_title(self, scientific_title):
        return self.vote_set.filter(scientific_title=scientific_title).count()

class Vote(models.Model):
    unvon = models.ForeignKey(IlmiyUnvon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scientific_title = models.CharField(max_length=20, choices=(('Xa', 'Xa'), ('yo\'q', 'Yo\'q'), ('betaraf', 'Betaraf')), default='betaraf', verbose_name='Ilmiy unvon')
   
    class Meta:
        verbose_name = "Ovoz berish"
        verbose_name_plural = "Ovoz berish"
        
    def vote_for_title(self, user, scientific_title):
        # Check if the user has already voted for this title
        existing_vote = Vote.objects.filter(user=user, unvon=self.unvon).exists()
        if existing_vote:
            return "You have already voted for this title."
        else:
            self.user = user
            self.scientific_title = scientific_title
            self.save()
            return "Vote successfully recorded."
        
class IlmiyUnvon(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    unvon = models.CharField(max_length=255, verbose_name='Ilmiy Unvon')
    name = models.CharField(max_length=255, verbose_name='Ism Familiya sharif')
    kaf = models.CharField(max_length=155, choices=fakultets, default=None, verbose_name='Fakulteti')

    def __str__(self):
        return self.unvon
    
    class Meta:
        verbose_name = "Ilmiy Unvon"
        verbose_name_plural = "Ilmiy Unvonlar"

    def count_votes_by_title(self):
        titles = dict(
            self.vote_set.values('scientific_title').annotate(vote_count=Count('id'))
        )
        return titles


class Vote(models.Model):
    unvon = models.ForeignKey(IlmiyUnvon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scientific_title = models.CharField(
        max_length=20,
        choices=(('Xa', 'Xa'), ('yoq', 'Yoq'), ('betaraf', 'Betaraf')),
        default='betaraf',
        verbose_name='Ilmiy unvon'
    )
   
    class Meta:
        verbose_name = "Ovoz berish"
        verbose_name_plural = "Ovoz berish"
        
    def vote_for_title(self, user, scientific_title):
        existing_vote = Vote.objects.filter(user=user, unvon=self.unvon).exists()
        if existing_vote:
            return "You have already voted for this title."
        else:
            self.user = user
            self.scientific_title = scientific_title
            self.save()
            return "Vote successfully recorded."