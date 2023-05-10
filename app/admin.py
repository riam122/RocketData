from django.contrib import admin

# Register your models here.
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from nested_inline.admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline

from app import models
from app.tasks import clear_the_debt

register_admin = admin.site.register


class EnterpriseTypeAdmin(admin.ModelAdmin):
    model = models.EnterpriseType
    ordering = ['id']
    list_display = ['type', ]
    fields = ['type', ]


register_admin(models.EnterpriseType, EnterpriseTypeAdmin)


class ProductsAdmin(admin.ModelAdmin):
    model = models.Products
    ordering = ['id']
    list_display = ['name', 'model', 'market_launch_date', ]
    fields = ['name', 'model', 'market_launch_date', ]


register_admin(models.Products, ProductsAdmin)


class EnterpriseEmployeesInline(NestedStackedInline):
    model = models.EnterpriseEmployees
    fields = [
        'user',
    ]
    extra = 1


class EnterpriseProductsInline(NestedStackedInline):
    model = models.EnterpriseProducts
    fields = [
        'products',
    ]
    extra = 1


class ProductsInline(admin.StackedInline):
    model = models.SupplyChainProducts
    fields = [
        'products',
    ]
    extra = 1


class CityFilter(admin.SimpleListFilter):
    title = 'City'
    parameter_name = 'city'

    try:
        enterprises = models.Enterprise.objects.all().values_list('city')
        cities = [city[0] for city in enterprises]
    except Exception as error:
        pass

    def lookups(self, request, model_admin):
        for city in self.cities:
            yield city, gettext_lazy(city)

    def queryset(self, request, queryset):
        value = self.value()
        if value not in self.cities:
            return None
        return queryset.filter(city=value)


class EnterpriseAdmin(NestedModelAdmin):
    change_form_template = 'admin/change_form_button.html'
    model = models.Enterprise
    ordering = "id",
    readonly_fields = 'provider', 'price', 'move_date',
    fields = [
        'name',
        'type',
        'provider',
        'price',
        'move_date',
        'email',
        ('country',
         'city',
         'the_outside',
         'house_number',
         )
    ]
    list_display = 'name', 'type'
    inlines = [
        EnterpriseProductsInline,
        EnterpriseEmployeesInline
    ]
    list_filter = [
        CityFilter,
    ]
    actions = [
        'clear_the_debt'
    ]

    query = ""

    def provider(self, obj):
        self.query = obj.recipient.filter(provider__level__lt=obj.level).last()
        provider = self.query.provider
        return mark_safe(
            f"<a href=http://127.0.0.1:8000/admin/app/enterprise/{provider.id}/change/ >"
            f"{provider}"
            f'</a>'
        )

    def price(self, obj):
        return self.query.price

    def move_date(self, obj):
        return self.query.move_date

    @admin.action(description='Сlear the debt')
    def clear_the_debt(self, request, queryset):
        if len(queryset) > 20:
            queryset = [x.pk for x in queryset]
            clear_the_debt.apply_async(
                args=(
                    queryset
                ),
                serializer='json',
            )
            return

        for qs in queryset:
            qs = qs.recipient.last()
            if not qs:
                return
            qs.price = 0
            qs.save()


register_admin(models.Enterprise, EnterpriseAdmin)


class SupplyChainAdmin(admin.ModelAdmin):
    model = models.SupplyChain
    readonly_fields = 'move_date',
    fields = 'provider', 'recipient', 'price', 'move_date'
    list_display = 'provider', 'recipient', 'price', 'move_date'
    inlines = [
        ProductsInline,
    ]


register_admin(models.SupplyChain, SupplyChainAdmin)
