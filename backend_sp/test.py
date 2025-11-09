import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_sp.settings')
django.setup()

from goods.models import Group

print("🔍 Перевіряю групи на цикли...\n")

for g in Group.objects.all():
    if g.parent_id == g.id:
        print(f"⚠️ Сам собі батько: {g.name}")

    if g.parent and g.parent.parent_id == g.id:
        print(f"⚠️ Цикл між: {g.name} <-> {g.parent.name}")

print("\n✅ Перевірка завершена")
