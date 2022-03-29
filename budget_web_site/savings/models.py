from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# Create your models here.
class Saving(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    amount = models.FloatField()  # decimal
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    type_saving = models.CharField(max_length=255)

    def __str__(self):
        return self.type_saving

    class Meta:
        ordering: ['-date']


class TypeSaving(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
