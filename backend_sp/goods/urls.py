from django.urls import path
from .views import all_products, index, products_by_group, product_detail

app_name = 'goods'

urlpatterns = [
    path("", index, name="index"),
    path('menu/', all_products, name='all_products'),  # всі товари
    path('menu/product/<slug:product_slug>/', product_detail, name='product_detail_no_group'),  # без групи
    path('menu/<slug:group_slug>/product/<slug:product_slug>/', product_detail, name='product_detail'),  # з групою
    path('menu/<slug:slug>/', products_by_group, name='products_by_group'),  # товари групи
]
