# Generated by Django 4.1.3 on 2023-04-27 13:51

from django.conf import settings
from django.db import migrations, models


def create(apps, schema_editor):
    Enterprise = apps.get_model('app', 'Enterprise')
    EnterpriseType = apps.get_model('app', 'EnterpriseType')
    list_enterprise = {
        'Завод1': [1, 0, 'asdf@as.as', 'Беларусь', "Минск", "Улица", "1"],
        'Дистрибьютор1': [2, 1, 'asdf1@as.as', 'Беларусь', "Гродно", "Улица", "1"],
        'Дилерский центр1': [3, 2, 'asdf2@as.as', 'Беларусь', "Витебск", "Улица", "1"],
        'Крупная розничная сеть1': [4, 3, 'asdf3@as.as','Россия', "Москва", "Улица", "1"],
        'Индивидуальный предприниматель1': [5, 4, 'asdf4@as.as','Россия', "Питер", "Улица", "1"],

    }
    list_query = []
    for name, data in list_enterprise.items():
        type = EnterpriseType.objects.get(pk=data[0])
        list_query.append(
            Enterprise(
                name=name,
                type=type,
                level=data[1],
                email=data[2],
                country=data[3],
                city=data[4],
                the_outside=data[5],
                house_number=data[-1],
            )
        )
    Enterprise.objects.bulk_create(list_query)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0004_products_remove_enterpriseemployees_name_and_more"),
    ]

    operations = [
        migrations.RunPython(create),
    ]
