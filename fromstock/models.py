from django.db import models
from organization.models import Organization



class ProductInStock(models.Model):
    datetime = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True, blank=True)
    user = models.ForeignKey("customuser.CustomUser", on_delete=models.CASCADE)

    def __str__(self):
        return f"#STK-{self.id} - For - {self.user.organization} --- Note - {self.note}"

    class Meta:
        verbose_name = 'Stock'

class ProductWithUnit(models.Model):
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    stock = models.ForeignKey(ProductInStock,on_delete=models.CASCADE)
    unit = models.FloatField()
    price = models.FloatField()
    datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("customuser.CustomUser", on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.id} -- For #STK -{self.stock.id}  --- {self.product}"

    class Meta:
        verbose_name = 'Products From Stock'
