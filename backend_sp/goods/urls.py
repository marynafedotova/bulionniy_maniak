from django.urls import path
from .views import all_products, index, products_by_group

app_name = 'goods'

urlpatterns = [
    path("", index, name="index"),
    path('menu/', all_products, name='all_products'),  # всі товари
    path('menu/<slug:slug>/', products_by_group, name='products_by_group'),  # товари групи
]
