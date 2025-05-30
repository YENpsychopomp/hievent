"""
URL configuration for hilifecoffee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from appcoffee import views
from appcoffee import exchange
from appcoffee import exchange

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path("getProducts/", views.getProducts),
    path("linePayUrl/", views.linePayUrl),
    path("payByCounter/", views.payByCounter),
    path("confirmTransactionID/", views.confirmTransactionID),
    path("linePayConfirmTransactionID/", views.linePayConfirmTransactionID),
    path("payByCounterTest/", views.payByCounterTest),
    path("exchange/", exchange.index),
    path("exchange/getProductInfo/", exchange.getProductInfo),
    path("exchange/share/", exchange.share),
    path("exchange/shares/", exchange.shares),
    path("exchange/sharesInit/", exchange.sharesInit),
    path("transactionBarcode/<str:code>.png", exchange.transactionBarcode, name="barcode_image"),
]