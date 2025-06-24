# professors/models.py

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

# --- Ma'lumotnoma modellar ---
class Kafedra(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Kafedra nomi")
    def __str__(self): return self.name
    class Meta: verbose_name = "Kafedra"; verbose_name_plural = "Kafedralar"; ordering = ['name']

class Lavozim(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Lavozim nomi")
    def __str__(self): return self.name
    class Meta: verbose_name = "Lavozim"; verbose_name_plural = "Lavozimlar"; ordering = ['name']

class Kengash(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Kengash nomi")
    def __str__(self): return self.name
    class Meta: verbose_name = "Kengash"; verbose_name_plural = "Kengashlar"

# --- Foydalanuvchi Profili Modeli ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Foydalanuvchi")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    surname = models.CharField(max_length=100, verbose_name="Otasining ismi")
    kafedra = models.ForeignKey(Kafedra, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kafedrasi")
    academic_degree = models.CharField(max_length=255, verbose_name="Ilmiy darajasi")
    position = models.CharField(max_length=255, verbose_name="Lavozimi")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqami")
    image = models.ImageField(upload_to='user_images/', blank=True, null=True, verbose_name="Rasmi")
    def __str__(self): return f"{self.user.last_name} {self.user.first_name}"
    class Meta: verbose_name = "Foydalanuvchi Profili"; verbose_name_plural = "Foydalanuvchi Profillari"

# ==========================================================
# 1. SAYLOV TIZIMI
# ==========================================================
class Saylov(models.Model):
    lavozim = models.ForeignKey(Lavozim, on_delete=models.CASCADE, verbose_name="Saylov lavozimi")
    title = models.CharField(max_length=255, verbose_name="Saylov sarlavhasi", help_text="Masalan, 'Fizika-matematika fakulteti dekanligi uchun saylov'")
    def __str__(self): return self.title
    class Meta: verbose_name = "Saylov"; verbose_name_plural = "Saylovlar"

class Tanlov(models.Model):
    saylov = models.ForeignKey(Saylov, on_delete=models.CASCADE, related_name='nomzodlar', verbose_name="Saylov")
    candidate_name = models.CharField(max_length=255, verbose_name="Nomzod (F.I.Sh)")
    def __str__(self): return f"{self.candidate_name} ({self.saylov.lavozim.name} uchun nomzod)"
    class Meta: verbose_name = "Saylov nomzodi"; verbose_name_plural = "Saylov nomzodlari"; ordering = ['candidate_name']

class SaylovVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saylov_votes')
    saylov = models.ForeignKey(Saylov, on_delete=models.CASCADE, related_name='votes')
    chosen_candidate = models.ForeignKey(Tanlov, on_delete=models.CASCADE, related_name='chosen_votes', verbose_name="Tanlangan nomzod")
    def clean(self):
        if self.chosen_candidate.saylov != self.saylov: raise ValidationError("Tanlangan nomzod ushbu saylovga tegishli emas.")
    def save(self, *args, **kwargs): self.clean(); super().save(*args, **kwargs)
    class Meta: unique_together = ('user', 'saylov'); verbose_name = "Saylov ovozi"; verbose_name_plural = "Saylov ovozlari"

# ==========================================================
# 2. STANDART OVOZ BERISH TIZIMI
# ==========================================================
class IlmiyUnvon(models.Model):
    candidate_name = models.CharField(max_length=255, verbose_name="Nomzod (F.I.Sh)")
    title = models.CharField(max_length=255, verbose_name="Beriladigan ilmiy unvon")
    title_code = models.CharField(max_length=255, verbose_name="Ilmiy unvon shifri")
    votes = GenericRelation('Vote')
    def __str__(self): return f"Unvon: {self.candidate_name} ({self.title})"
    class Meta: verbose_name = "Ilmiy Unvon uchun nomzod"; verbose_name_plural = "Ilmiy Unvon uchun nomzodlar"

class BoshqaMasala(models.Model):
    title = models.CharField(max_length=255, verbose_name="Masala sarlavhasi")
    description = models.TextField(verbose_name="Masala tavsifi", blank=True)
    votes = GenericRelation('Vote')
    def __str__(self): return f"Masala: {self.title}"
    class Meta: verbose_name = "Boshqa masala"; verbose_name_plural = "Boshqa masalalar"

class Vote(models.Model):
    class OvozChoices(models.TextChoices):
        HA = 'ha', "Ha"
        YOQ = 'yoq', "Yo'q"
        BETARAF = 'betaraf', "Betaraf"
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    ovoz = models.CharField(max_length=10, choices=OvozChoices.choices)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    class Meta: verbose_name = "Standart Ovoz"; verbose_name_plural = "Standart Ovozlar"; unique_together = ('user', 'content_type', 'object_id')

# ==========================================================
# MARKAZIY BYULLETEN MODELI
# ==========================================================
class Byulleten(models.Model):
    kengash = models.ForeignKey(Kengash, on_delete=models.CASCADE, related_name='byulletenlar')
    title = models.CharField(max_length=255, verbose_name="Byulleten sarlavhasi")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Ovoz berish uchun ochiqmi?")
    start_time = models.DateTimeField(verbose_name="Ochilish vaqti", null=True, blank=True)
    end_time = models.DateTimeField(verbose_name="Yopilish vaqti", null=True, blank=True)
    saylovlar = models.ManyToManyField(Saylov, blank=True, related_name="byulletenlar", verbose_name="Saylovlar")
    unvonlar = models.ManyToManyField(IlmiyUnvon, blank=True, related_name="byulletenlar", verbose_name="Ilmiy unvonlar")
    boshqa_masalalar = models.ManyToManyField(BoshqaMasala, blank=True, related_name="byulletenlar", verbose_name="Boshqa masalalar")
    allowed_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="accessible_ballots",
        verbose_name="Ruxsat etilgan foydalanuvchilar",
        help_text="Ushbu byulletenga faqat shu ro'yxatdagi foydalanuvchilar kira oladi. Agar bo'sh qoldirilsa, hech kim kira olmaydi."
    )
    def __str__(self): return f"{self.title} ({self.kengash.name})"
    class Meta:
        verbose_name = "Byulleten"
        verbose_name_plural = "Byulletenlar"
        ordering = ['-created_at']