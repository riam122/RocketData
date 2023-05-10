"""RocketData URL Configuration

The `urlpatterns` list routes URLs to views.py. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views.py
    1. Add an import:  from my_app import views.py
    2. Add a URL to urlpatterns:  path('', views.py.home, name='home')
Class-based views.py
    1. Add an import:  from other_app.views.py import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from app.api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),

    path('api/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    path('custom/qr/<str:name_enterprise>', views.QrView.as_view()),

    path('custom/my_enterprise', views.EnterpriseView.as_view()),

    path('custom/list_enterprise', views.ListEnterpriseView.as_view()),
    path('custom/list_enterprise_from_country/<str:country>/', views.EnterpriseFromCountryView.as_view()),
    path('custom/list_enterprise_statistics', views.StatisticsEnterpriseView.as_view()),
    path('custom/list_enterprise_product/<int:product_id>/', views.ProductsEnterpriseView.as_view()),

    path('custom/add_product', views.ProductsView.as_view()),
    path('custom/update_product/<str:product_name>/', views.UpdateProductView.as_view()),
    path('custom/delete_product/<str:product_name>/', views.DeleteProductsView.as_view()),

    path('custom/add_supply_chain/', views.SupplyChainView.as_view()),
    path('custom/update_supply_chain/<str:provider_name>/<str:recipient_name>', views.UpdateSupplyChainView.as_view()),
    path('custom/delete_supply_chain/<str:provider_name>/<str:recipient_name>/', views.DeleteSupplyChainView.as_view()),
]

