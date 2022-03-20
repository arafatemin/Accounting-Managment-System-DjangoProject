from django.db import models




class UnitType(models.Model):
    note         = models.TextField(null=True,blank=True)
    name         = models.CharField(max_length=64,unique=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    title               = models.CharField(max_length=64,unique=True)
    note                = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.title




class BaseProduct(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    name = models.CharField(max_length=64, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True)
    barcode = models.CharField(max_length=64)
    datetime    = models.DateTimeField(auto_now_add=True)
    note        = models.TextField(max_length=512,null=True,blank=True)


    def __str__(self):
        return f"{self.id} - SKU - {self.sku}  ---  {self.name}"



class Product(models.Model):
    organization= models.ForeignKey("organization.Organization",on_delete=models.SET_NULL,null=True)
    product     = models.ForeignKey("BaseProduct",on_delete=models.SET_NULL,null=True)
    price       = models.FloatField()
    sell_price  = models.FloatField()

    def __str__(self):
        return f"Imported Product {self.id} - BaseProduct - {self.product.id} - SKU - {self.product.sku} - {self.product.name}  ------ ORG - {self.organization.name}"


    class Meta:
        verbose_name = 'Imported Product'
