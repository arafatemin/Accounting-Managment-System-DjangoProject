from django.db import models
from organization.models import Organization

class Return(models.Model):
    datetime = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True, blank=True)
    user = models.ForeignKey("customuser.CustomUser", on_delete=models.CASCADE)
    customer = models.ForeignKey("customer.Customer",on_delete=models.CASCADE,related_name='return_customer',null=True,blank=True)

    def __str__(self):
        return f"#RTN-00{self.id}  - {self.datetime.strftime('%Y-%m-%d %H:%M:%S')} --- For - {self.user.organization}"



class ReturnWithUnit(models.Model):
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    returned = models.ForeignKey(Return,on_delete=models.CASCADE)
    unit = models.FloatField()
    price = models.FloatField()
    datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("customuser.CustomUser", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}  -  For - {self.returned}  ---  {self.product}"

class ReturnPayment(models.Model):
    returned            = models.ForeignKey(Return,on_delete=models.CASCADE)
    bank                = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING,related_name='return_payment_bank')
    date                = models.DateTimeField(auto_now=True)
    amount              = models.FloatField()
    note                = models.TextField(null=True,blank=True)
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='return_payment_user')

    def __str__(self):
        return f"{self.id} --- Payment for - #RTN-0{self.returned.id}---Amount - {self.amount} SAR --- For - {self.bank}"


    class Meta:
        verbose_name = 'Payments For Return'