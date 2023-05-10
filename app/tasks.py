import random
import qrcode
import smtplib

from django.conf import settings
from django.db import transaction
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from RocketData.celery import celery_app
from app.models import SupplyChain, Enterprise


@celery_app.task
def add_price():
    supply_chains = SupplyChain.objects.filter(price__gt=0)
    for supply_chain in supply_chains:
        with transaction.atomic():
            supply_chain.price += random.uniform(5, 500)
            supply_chain.save()


@celery_app.task
def take_away_the_price():
    supply_chains = SupplyChain.objects.filter(price__gt=0)
    for supply_chain in supply_chains:
        with transaction.atomic():
            supply_chain.price -= random.uniform(100, 10_000)
            supply_chain.save()


@celery_app.task
def clear_the_debt(queryset: list[id]):
    if not isinstance(queryset, list):
        queryset = [queryset]

    queryset = Enterprise.objects.filter(pk__in=queryset)
    for enterprise in queryset:
        enterprise = enterprise.recipient.last()
        enterprise.price = 0
        enterprise.save()


@celery_app.task
def send_email(data: str, name_enterprise: str, user_email: str):
    path = "some_file.png"
    img = qrcode.make(data)
    img.save(path)

    with open(path, 'rb') as fp:
        file = MIMEImage(fp.read())

    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = user_email
    msg['Subject'] = f'QR from {name_enterprise}'
    file.add_header('Content-Disposition', 'attachment', filename=path)

    msg.attach(file)
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.set_debuglevel(True)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.send_message(msg)
    server.quit()
