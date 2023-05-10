from django.db.models.signals import post_save
from django.dispatch import receiver

from app import models


@receiver(post_save, sender=models.SupplyChainProducts)
def supply_chain_product(**kwargs):
    instance = kwargs['instance']
    created = kwargs['created']

    if created:
        recipient = models.SupplyChain.objects.get(products_supply_chain=instance).recipient
        product = instance.products.products
        models.EnterpriseProducts.objects.create(
            enterprise=recipient,
            products=product
        )
