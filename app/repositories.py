from typing import Union, Optional

from django.db import IntegrityError

from app import models
from app.schemas.datetime import ValidDate


class CheckValid:
    @staticmethod
    def product_name(*, name: str) -> Optional[str]:
        if len(name) > 25:
            return f"404 product name {name} must not exceed 25 characters"

    @staticmethod
    def product(*, name: str) -> Union[str, models.Products]:
        try:
            product = models.Products.objects.get(name=name)
        except models.Products.DoesNotExist:
            return f"404 there is no product with this name {name}"
        return product

    @staticmethod
    def date(*, date: str) -> Optional[str]:
        try:
            ValidDate.parse_obj({'date': date})
        except ValueError:
            return f"404 written given in the wrong format {date}"
        return

    @staticmethod
    def name_enterprise(*, name: str) -> Optional[str]:
        if len(name) > 50:
            return f"404 provider or recipient name {name} must not exceed 50 characters"
        return

    @classmethod
    def name_enterprises(cls, *, name1: str, name2: str) -> Optional[str]:

        error_enterprise_name = cls.name_enterprise(name=name1)
        if isinstance(error_enterprise_name, str):
            return error_enterprise_name

        error_enterprise_name = cls.name_enterprise(name=name2)
        if isinstance(error_enterprise_name, str):
            return error_enterprise_name

    @staticmethod
    def enterprise(*, name: str) -> Union[str, models.Enterprise]:
        try:
            enterprise = models.Enterprise.objects.get(name=name)
        except models.Enterprise.DoesNotExist:
            return f"404 there is no enterprise with this name {name}"
        return enterprise

    @classmethod
    def enterprises(cls, *, provider: str, recipient: str
                    ) -> Union[str, tuple[models.Enterprise, models.Enterprise]]:
        provider_or_error = cls.enterprise(name=provider)
        if isinstance(provider_or_error, str):
            return provider_or_error

        recipient_or_error = cls.enterprise(name=recipient)
        if isinstance(recipient_or_error, str):
            return recipient_or_error

        return provider_or_error, recipient_or_error

    @classmethod
    def supply_chain(cls, *, provider_name: str, recipient_name: str
                     ) -> Union[str, models.SupplyChain]:

        error_or_enterprises = CheckValid.enterprises(
            provider=provider_name,
            recipient=recipient_name,
        )

        if isinstance(error_or_enterprises, str):
            return error_or_enterprises

        provider, recipient = error_or_enterprises

        try:
            supply_chain = models.SupplyChain.objects.get(provider=provider, recipient=recipient)
        except models.SupplyChain.DoesNotExist:
            return f"404 there is not supply chain {provider} - {recipient}"
        return supply_chain


class CheckSave:
    @staticmethod
    def product(*, product: models.Products) -> Union[str, models.Products]:
        try:
            product.save()
        except IntegrityError:
            return f"404 product with the same name{product} already exists"
        return product

    @staticmethod
    def supply_chain(*, supply_chain: models.SupplyChain) -> Union[str, models.SupplyChain]:
        try:
            supply_chain.save()
        except IntegrityError:
            return f"404 such {supply_chain} network already exists"
        return supply_chain


class Products:

    @staticmethod
    def set_name(*, new_name: str, product: models.Products):
        product.name = new_name if (
                new_name != product.name and new_name != "" and new_name != "string"
        ) else product.name

    @staticmethod
    def set_model(*, new_model: str, product: models.Products):
        product.model = new_model if (
                new_model != product.model and new_model != "" and new_model != "string"
        ) else product.model

