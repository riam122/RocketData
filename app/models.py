from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class EnterpriseType(models.Model):
    type = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.type


class Enterprise(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['level'],
                name='level_idx',
            ),
        ]

    name = models.CharField(max_length=50, unique=True)
    type = models.ForeignKey(EnterpriseType, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(max_length=32)
    country = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    the_outside = models.CharField(max_length=32)
    house_number = models.CharField(max_length=32)
    level = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.level = self.type.id - 1 if self.level != -1 else -1
        super().save(*args, **kwargs)


class Products(models.Model):
    name = models.CharField(max_length=25, unique=True)
    model = models.CharField(max_length=64)
    market_launch_date = models.DateTimeField()

    def __str__(self):
        return self.name


class EnterpriseProducts(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=['products'],
                name='enterprise_products_idx',
            ),
            models.Index(
                fields=['enterprise'],
                name='products_enterprise_idx',
            ),
        ]

    products = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='enterprise')
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.products.name


class EnterpriseEmployees(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='enterprise_user')
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, related_name='user')


class SupplyChain(models.Model):
    class Meta:
        unique_together = (("provider", "recipient"),)
        indexes = [
            models.Index(
                fields=['price'],
                name='price_idx',
            ),
            models.Index(
                fields=['recipient'],
                name='supply_chain_recipient_idx',
            ),
        ]

    provider = models.ForeignKey(Enterprise, on_delete=models.PROTECT, related_name='provider')
    recipient = models.ForeignKey(Enterprise, on_delete=models.PROTECT, related_name='recipient')
    price = models.FloatField(null=True, blank=True)
    move_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.price is not None:
            self.price = round(self.price, 2)
        self.price = 0 if self.price < 0 else self.price
        if self.provider.level == 0 and self.recipient.level == 3:
            self.recipient.level = -1
            self.recipient.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.provider.name} - {self.recipient.name} '


class SupplyChainProducts(models.Model):
    supply_chain = models.ForeignKey(SupplyChain, on_delete=models.CASCADE, related_name='products_supply_chain')
    products = models.ForeignKey(EnterpriseProducts, on_delete=models.CASCADE, related_name='supply_chain')
