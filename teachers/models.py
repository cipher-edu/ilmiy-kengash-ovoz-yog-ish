from django.db import models

# Create your models here.
class Teacher(models.Model):
    name = models.CharField(max_length=250)
    fristname =  models.CharField(max_length=250)
    lavozimi = models.CharField(max_length=250)
    ish_joyi = models.CharField(max_length=250)
    number = models.IntegerField()



    # def __str__(self):
    #     return f" {self.name} "