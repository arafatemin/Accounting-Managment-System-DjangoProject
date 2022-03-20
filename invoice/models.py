from django.db import models





class Invoice(models.Model):
    note                = models.TextField(null=True,blank=True)
    customer            = models.ForeignKey("customer.Customer",on_delete=models.CASCADE,related_name='invoice_customer',null=True,blank=True)
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='invoice_user')
    datetime            = models.DateTimeField(auto_now=True)
    tax                 = models.ForeignKey("tax.Tax",on_delete=models.CASCADE)

    def __str__(self):
        return f"#INV-00{self.id}  ------   {self.datetime.strftime('%Y-%m-%d %H:%M:%S')} - For - {self.customer}"


class SoldProduct(models.Model):
    product         = models.ForeignKey("product.Product",on_delete=models.CASCADE)
    unit            = models.FloatField()
    price           = models.FloatField()
    datetime        = models.DateTimeField(auto_now=True)
    user            = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE)
    invoice         = models.ForeignKey("Invoice", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.product} --- For - #INV-00{self.invoice.id} --- Price - {self.price} SAR "


    class Meta:
        verbose_name = 'Products In Invoice'




class ReturnedProduct(models.Model):
    sold_product    = models.ForeignKey("SoldProduct", on_delete=models.CASCADE)
    datetime        = models.DateTimeField(auto_now=True)
    note            = models.TextField(null=True,blank=True)


class Payment(models.Model):
    invoice             = models.ForeignKey(Invoice,on_delete=models.CASCADE)
    bank              = models.ForeignKey('bank.Bank',on_delete=models.DO_NOTHING,related_name='invoice_payment_bank')
    date                = models.DateTimeField(auto_now=True)
    amount              = models.FloatField()
    note                = models.TextField(null=True,blank=True)
    user                = models.ForeignKey("customuser.CustomUser",on_delete=models.CASCADE,related_name='payment_INVOICE_user')

    def __str__(self):
        return f"{self.id} --- Payment for - #INV-0{self.invoice.id}---Amount - {self.amount} SAR --- For - {self.bank}"


    class Meta:
        verbose_name = 'Payments For Invoice'

