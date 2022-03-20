from django.db import models






class Purchase(models.Model):
    note                = models.TextField(null=True,blank=True)
    customer            = models.ForeignKey("vendor.Vendor",on_delete=models.CASCADE,related_name='purchase_vendor',null=True,blank=True)
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='purchase_user')
    datetime            = models.DateTimeField(auto_now=True)
    tax                 = models.ForeignKey("tax.Tax",on_delete=models.CASCADE)

    def __str__(self):
        return f"#PUR-00{self.id}  ------   {self.datetime.strftime('%Y-%m-%d %H:%M:%S')} --- From - {self.customer}"


class BoughtProduct(models.Model):
    product         = models.ForeignKey("product.Product",on_delete=models.CASCADE)
    unit            = models.FloatField()
    price           = models.FloatField()
    datetime        = models.DateTimeField(auto_now=True)
    user            = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE)
    purchase         = models.ForeignKey("Purchase", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.product} - For - #PUR-0{self.purchase.id} --- Price - {self.price} SAR "

    class Meta:
        verbose_name = 'Products In Purchase'




class ReturnedProduct(models.Model):
    bought_product    = models.ForeignKey("BoughtProduct", on_delete=models.CASCADE)
    datetime        = models.DateTimeField(auto_now=True)
    note            = models.TextField(null=True,blank=True)


class Debt(models.Model):
    note = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now=True)
    customer            = models.ForeignKey("vendor.Vendor",on_delete=models.CASCADE,related_name='debt_vendor',null=True,blank=True)
    user                 = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='debt')

    def __str__(self):
            return f"#DBT 00{self.id}-Amount - {self.amount} SAR --- For - {self.customer}"


    class Meta:
        verbose_name = 'Vendor Debt'

class Payment(models.Model):
    purchase             = models.ForeignKey(Purchase,on_delete=models.CASCADE)
    bank                 = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING)
    date                 = models.DateTimeField(auto_now=True)
    amount               = models.FloatField()
    note                 = models.TextField(null=True,blank=True)
    user                 = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='payment_user')

    def __str__(self):
        return f"{self.id} --- Payment for - #PUR-0{self.purchase.id}---Amount - {self.amount} SAR --- For - {self.bank.name} - {self.bank.organization.name}"


    class Meta:
        verbose_name = 'Vendor Payment'


class DebtPayment(models.Model):
    debt                 = models.ForeignKey(Debt,on_delete=models.CASCADE)
    bank                 = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING)
    date                 = models.DateTimeField(auto_now=True)
    amount               = models.FloatField()
    note                 = models.TextField(null=True,blank=True)
    user                 = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='debt_payment_user')

    def __str__(self):
        return f"{self.id} --- Payment for - {self.debt}"

    class Meta:
        verbose_name = 'Vendor Debt Payment'