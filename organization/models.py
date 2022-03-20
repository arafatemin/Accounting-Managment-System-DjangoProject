from django.db import models
from bank.models import Bank
from django.db.models import signals
from django.dispatch import Signal
from city.models import City






class Organization(models.Model):
    name            = models.CharField(max_length=64,unique=True)
    email           = models.EmailField()
    phone           = models.CharField(max_length=32)
    city            = models.ForeignKey(City,on_delete=models.DO_NOTHING,related_name="cities",null=True,blank=True)
    address         = models.TextField()
    note            = models.TextField(null=True,blank=True)


    def __str__(self):
        return f"{self.name}"


def organization_model_post_save(sender, instance, created, *args, **kwargs):
    if created:
        Bank.objects.create(organization=instance,name='نقد')

signals.post_save.connect(receiver=organization_model_post_save,sender=Organization)
