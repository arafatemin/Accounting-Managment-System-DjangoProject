from django.db import models


class City(models.Model):
    name = models.CharField(max_length=128, unique=True)
    note = models.TextField(max_length=512, null=True, blank=True)

    def __str__(self):
        return f"{self.id} ---  {self.name}"
