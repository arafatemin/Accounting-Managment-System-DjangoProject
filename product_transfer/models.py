from django.db import models
from organization.models import Organization



class ProductTransfer(models.Model):
    from_org = models.ForeignKey(Organization,on_delete=models.DO_NOTHING,related_name='transfer_from')
    to_org = models.ForeignKey(Organization,on_delete=models.DO_NOTHING,related_name='transfer_to')
    datetime = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True,blank=True)
    tax = models.ForeignKey("tax.Tax",on_delete=models.CASCADE)
    user = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE)

    def __str__(self):
        return f"#TRA-0{self.id} - From -  {self.from_org.name} - To - {self.to_org.name} - Date - {self.datetime.strftime('%Y-%m-%d %H:%M:%S')} - Note - {self.note}"


class OrgDebt(models.Model):
    note                = models.TextField(null=True, blank=True)
    amount              = models.FloatField()
    date                = models.DateTimeField(auto_now=True)
    organization        = models.ForeignKey("organization.Organization",on_delete=models.CASCADE,related_name='org_debt_org')
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='org_debt_user')

    def __str__(self):
            return f"#DBT 00{self.id}-Amount - {self.amount} SAR --- For - {self.organization}"

    class Meta:
        verbose_name = 'Organization Debt'

class OrgDebtPayment(models.Model):
    debt                 = models.ForeignKey(OrgDebt,on_delete=models.CASCADE)
    from_bank                 = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING,related_name='org_from_bank')
    to_bank                 = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING,related_name='org_to_bank')
    date                 = models.DateTimeField(auto_now=True)
    amount               = models.FloatField()
    note                 = models.TextField(null=True,blank=True)
    user                 = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='org_debt_payment_user')

    def __str__(self):
        return f"{self.id} --- Payment for - {self.debt}"

    class Meta:
        verbose_name = 'Organization Debt Payment'

class TransferPayment(models.Model):
    amount = models.FloatField()
    datetime =models.DateTimeField(auto_now=True)
    from_bank     = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING,null=True,blank=True,related_name='out_payment')
    to_bank     = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING,null=True,blank=True,related_name='in_payment')
    transfer = models.ForeignKey(ProductTransfer,on_delete=models.CASCADE)
    note = models.TextField(null=True,blank=True)
    user = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='payment_transfer_user')

    def __str__(self):
        return f"Payment {self.id} - For - #TRA-0{self.transfer.id} - Amount - {self.amount} SAR "

class TransferedProduct(models.Model):
    product = models.ForeignKey("product.Product",on_delete=models.CASCADE)
    transfer = models.ForeignKey(ProductTransfer,on_delete=models.CASCADE)
    unit = models.FloatField()
    datetime = models.DateTimeField(auto_now=True)
    price = models.FloatField()
    user = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product} - Unit - {self.unit}  {self.product.product.type.name} - Amount - {self.price} SAR   -- For - {self.transfer}"


class TransferReturnedProduct(models.Model):
    product    = models.ForeignKey("TransferedProduct", on_delete=models.CASCADE)
    datetime        = models.DateTimeField(auto_now=True)
    note            = models.TextField(null=True,blank=True)
