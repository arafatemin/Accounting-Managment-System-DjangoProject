from django.db import models





class Customer(models.Model):
    name                = models.CharField(max_length=64,unique=True)
    phone_number        = models.CharField(max_length=16,null=True,blank=True)
    email               = models.EmailField(null=True,blank=True)
    address             = models.TextField(null=True,blank=True)
    belongs_to          = models.ForeignKey("organization.Organization",on_delete=models.CASCADE,related_name='customer_belongs_to')
    note                = models.TextField(null=True,blank=True)

    def __str__(self):
        return f"{self.id} --- {self.name}   --- for - {self.belongs_to.name}"
