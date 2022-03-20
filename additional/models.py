from django.db import models





class OutcomeCategory(models.Model):
    name             = models.CharField(max_length=256,unique=True)
    note             = models.TextField(max_length=512,null=True,blank=True)
    user             = models.ForeignKey("customuser.CustomUser",on_delete=models.DO_NOTHING,related_name='out_cat_user')

    def __str__(self):
        return f"{self.id} -- {self.name}"


class AdditionalOutcomes(models.Model):
    amount              = models.FloatField()
    note                = models.TextField(null=True,blank=True)
    datetime            = models.DateTimeField(auto_now_add=True)
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.DO_NOTHING,related_name='a_o_user')
    bank              = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING)
    category            = models.ForeignKey("OutcomeCategory", on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return f"#OUT 00{self.id} -- {self.amount} SAR  --- From - {self.bank} -- Note  --  {self.note}"

    class Meta:
        ordering = ['-datetime']


class IncomeCategory(models.Model):
    name             = models.CharField(max_length=256,unique=True)
    note             = models.TextField(max_length=512,null=True,blank=True)
    user             = models.ForeignKey("customuser.CustomUser",on_delete=models.DO_NOTHING,related_name='income_cat_user')

    def __str__(self):
        return f"{self.id} -- {self.name}"

class AdditionalIncomes(models.Model):
    amount              = models.IntegerField()
    note                = models.TextField()
    datetime                = models.DateTimeField(auto_now_add=True)
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='ai_user')
    bank              = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING)
    category            = models.ForeignKey("IncomeCategory", on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return f"#INC-0{self.id} -- {self.amount} SAR -- For -- {self.bank} -- Note  --  {self.note}"

