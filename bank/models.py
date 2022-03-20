from django.db import models



class Bank(models.Model):
    iban                = models.CharField(max_length=32,null=True,blank=True)
    name                = models.CharField(max_length=64)
    note                = models.TextField(null=True,blank=True)
    organization        = models.ForeignKey("organization.Organization",on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}           --- ORG  --- {self.organization.name}"



class Transfer(models.Model):
    from_account        = models.ForeignKey(Bank,on_delete=models.CASCADE,related_name='out_transfer',null=True,blank=True)
    to_account          = models.ForeignKey(Bank, on_delete=models.CASCADE,related_name='in_trnafer',null=True,blank=True)
    date                = models.DateTimeField(auto_now=True)
    amount              = models.FloatField()
    note                = models.TextField(null=True, blank=True)
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='money_transfer_user')

    def __str__(self):
        return f"{self.id} --- From - {self.from_account} --- To - {self.to_account} ---- Amount -{self.amount} SAR"


    class Meta:
        verbose_name = 'Money Transfers'
