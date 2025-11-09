from django.shortcuts import render, get_object_or_404
from .models import Group, Product

def index(request):
    return render(request, "goods/index.html")

def all_products(request):
    products = Product.objects.filter(is_included_in_menu=True)
    groups = Group.objects.filter(is_included_in_menu=True, parent__isnull=True).order_by('order')
    context = {
        'products': products,
        'groups': groups,  # для меню
    }
    return render(request, "goods/all_products.html", context)


def products_by_group(request, slug):
    group = get_object_or_404(Group, slug=slug)

    # Основні продукти
    products = Product.objects.filter(group=group, is_included_in_menu=True, type=Product.DISH)

    # Якщо це група модифікаторів — показати модифікатори
    modifiers = Product.objects.filter(group=group, type=Product.MODIFIER)

    context = {
        "group": group,
        "products": products,
        "modifiers": modifiers,
    }
    return render(request, "goods/group_products.html", context)
