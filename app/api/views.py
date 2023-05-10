from django.db.models import Avg
from django.contrib.auth.models import User

from django.http import HttpResponse
from rest_framework import views
from rest_framework.permissions import IsAuthenticated

from app.api import serializer
from app import models
from rest_framework.response import Response

from app.repositories import CheckValid, CheckSave, Products
from app.tasks import send_email


class ProductsView(views.APIView):
    serializer_class = serializer.ProductsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data

        error = CheckValid.product_name(name=data.get("name"))
        if isinstance(error, str):
            return HttpResponse(error)

        error = CheckValid.date(date=data.get("market_launch_date"))
        if isinstance(error, str):
            return HttpResponse(error)

        product = models.Products(name=data.get("name"), model=data.get("model"),
                                  market_launch_date=data.get("market_launch_date"))

        error = CheckSave.product(product=product)
        if isinstance(error, str):
            return HttpResponse(error)

        return HttpResponse("200")


class UpdateProductView(views.APIView):
    serializer_class = serializer.UpdateProductsSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, product_name: str, *args, **kwargs):
        data = request.data

        error = CheckValid.product_name(name=product_name)
        if isinstance(error, str):
            return HttpResponse(error)

        error_or_product = CheckValid.product(name=product_name)
        if isinstance(error_or_product, str):
            return HttpResponse(error_or_product)
        product = error_or_product

        error = CheckValid.date(date=data.get("new_market_launch_date"))
        if isinstance(error, str):
            return HttpResponse(error)

        Products.set_name(new_name=data.get("new_name"), product=product)
        Products.set_model(new_model=data.get("new_model"), product=product)

        product.market_launch_date = data.get("new_market_launch_date")

        error = CheckSave.product(product=product)
        if isinstance(error, str):
            return HttpResponse(error)

        return HttpResponse("200")


class DeleteProductsView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, product_name: str, *args, **kwargs):
        error_or_product = CheckValid.product(name=product_name)
        if isinstance(error_or_product, str):
            return HttpResponse(error_or_product)
        error_or_product.delete()
        return HttpResponse("200")


class SupplyChainView(views.APIView):
    serializer_class = serializer.SupplyChainViewSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data

        error_enterprise_name = CheckValid.name_enterprises(
            name1=data.get("provider"),
            name2=data.get("recipient"),
        )

        if isinstance(error_enterprise_name, str):
            return HttpResponse(error_enterprise_name)

        error_or_enterprises = CheckValid.enterprises(
            provider=data.get("provider"),
            recipient=data.get("recipient"),
        )

        if isinstance(error_or_enterprises, str):
            return HttpResponse(error_or_enterprises)

        provider, recipient = error_or_enterprises

        error = CheckValid.date(date=data.get("move_date"))
        if isinstance(error, str):
            return HttpResponse(error)

        supply_chain = models.SupplyChain(
            provider=provider,
            recipient=recipient,
            price=data.get("price"),
            move_date=data.get("move_date")
        )

        error = CheckSave.supply_chain(supply_chain=supply_chain)
        if isinstance(error, str):
            return HttpResponse(error)

        return HttpResponse("200")


class UpdateSupplyChainView(views.APIView):
    serializer_class = serializer.UpdateSupplyChainViewSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, provider_name: str, recipient_name: str, *args, **kwargs):
        data = request.data

        error_enterprise_name = CheckValid.name_enterprises(
            name1=data.get("new_provider"),
            name2=data.get("new_recipient"),
        )

        if isinstance(error_enterprise_name, str):
            return HttpResponse(error_enterprise_name)

        error_or_supply = CheckValid.supply_chain(
            provider_name=provider_name,
            recipient_name=recipient_name
        )
        if isinstance(error_or_supply, str):
            return HttpResponse(error_or_supply)
        supply_chain = error_or_supply

        error_or_enterprises = CheckValid.enterprises(
            provider=data.get("new_provider"),
            recipient=data.get("new_recipient"),
        )

        if isinstance(error_or_enterprises, str):
            return HttpResponse(error_or_enterprises)

        provider, recipient = error_or_enterprises

        error = CheckValid.date(date=data.get("new_move_date"))
        if isinstance(error, str):
            return HttpResponse(error)

        supply_chain.provider = provider
        supply_chain.recipient = recipient
        supply_chain.move_date = data.get('new_move_date')

        error = CheckSave.supply_chain(supply_chain=supply_chain)
        if isinstance(error, str):
            return HttpResponse(error)

        return HttpResponse("200")


class DeleteSupplyChainView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, provider_name: str, recipient_name: str, *args, **kwargs):
        error_or_supply = CheckValid.supply_chain(
            provider_name=provider_name,
            recipient_name=recipient_name
        )
        if isinstance(error_or_supply, str):
            return HttpResponse(error_or_supply)
        supply_chain = error_or_supply

        supply_chain.delete()
        return HttpResponse("200")


class EnterpriseView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(get_data_for_enterprise(list(models.Enterprise.objects.filter(user__user=request.user))))


class ListEnterpriseView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(get_data_for_enterprise(list(models.Enterprise.objects.filter(recipient__price__gt=0))))


class EnterpriseFromCountryView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, country, *args, **kwargs):
        return Response(get_data_for_enterprise(
            list(models.Enterprise.objects.filter(country=country))))


class StatisticsEnterpriseView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        average_debt = models.SupplyChain.objects.all().aggregate(Avg('price'))['price__avg']
        list_enterprise_statistics = get_data_for_enterprise(
            list(
                models.Enterprise.objects.filter(recipient__price__gt=average_debt)
            )
        )
        if len(list_enterprise_statistics) == 0:
            return HttpResponse("200 There are no enterprises with more than average debt")
        return Response(list_enterprise_statistics)


class ProductsEnterpriseView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, product_id: int, *args, **kwargs):
        return Response(
            get_data_for_enterprise(
                list(models.Enterprise.objects.filter(products__products=product_id).all())
            )
        )


def get_data_for_enterprise(enterprises: list[models.Enterprise]) -> list[list[dict]]:
    list = []
    for enterprise in enterprises:
        enterprise_data = serializer.EmployeesSerializer(
            enterprise
        )
        products_data = serializer.ProductsSerializer(
            models.Products.objects.filter(enterprise__enterprise=enterprise), many=True
        )
        employees_data = serializer.EnterpriseEmployeesSerializer(
            User.objects.filter(enterprise_user__enterprise=enterprise), many=True
        )
        provider = enterprise.recipient.filter(provider__type__id__lt=enterprise.type.id).last()
        provider_data = serializer.SupplyChainSerializer(provider) if provider else None
        list.append(
            [
                {'enterprise': enterprise_data.data},
                {'products': products_data.data},
                {'employees': employees_data.data},
                {'debt': provider_data.data if provider_data else None}
            ]
        )

    return list


class QrView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, name_enterprise: str, *args, **kwargs):
        error_or_enterprise = CheckValid.enterprise(name=name_enterprise)
        if isinstance(error_or_enterprise, str):
            return HttpResponse(error_or_enterprise)
        enterprise = error_or_enterprise

        data = f'email:{enterprise.email}\n' \
               f'Address:{enterprise.country}-{enterprise.city}-{enterprise.the_outside}-{enterprise.house_number}'
        user_email = request.user.email

        send_email.apply_async(
            args=(
                data,
                name_enterprise,
                user_email,
            ),
            serializer='json',
        )
        return HttpResponse("200")
