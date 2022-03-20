from django.db import models





class Tax(models.Model):
    note                = models.TextField(null=True,blank=True)
    percent             = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.percent} % "