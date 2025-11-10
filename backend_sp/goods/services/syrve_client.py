import os
import requests
import time
import uuid
from  slugify import slugify
from dotenv import load_dotenv, find_dotenv

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_sp.settings')
django.setup()


from goods.models import Product, ProductCategory, Group, GroupModifier, GroupModifierChild


load_dotenv(find_dotenv())

class SyrveClient:
    def __init__(self):
        self.api_key = os.getenv("APIKEY")
        self.base_url = os.getenv("BASE_URL")
        self.org_id = os.getenv("ORG_ID")
        self.term_grp = os.getenv("TERMINAL_GROUP_ID")
        self.org_id_cache = None 
        self.token_cache = None
        self.token_created_at = None
        self.token_ttl = 3600

    def get_token(self):
        # якщо токен ще живий — повертаємо кешований
        if self.token_cache and (time.time() - self.token_created_at) < self.token_ttl:
            return self.token_cache

        # якщо ні — отримуємо новий
        url = f"{self.base_url}/api/1/access_token"
        payload = {"apiLogin": self.api_key}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            self.token_cache = token
            self.token_created_at = time.time()
            return token
        else:
            raise Exception(f"Syrve auth error: {response.status_code} {response.text}")


    def get_token(self):
        url = f"{self.base_url}/api/1/access_token"
        payload = {"apiLogin": self.api_key}
        response = requests.post(url, json=payload)


        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            return token
        else:
            raise Exception(f"Syrve auth error: {response.status_code} {response.text}")


    def get_menu(self):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        body = {
            "organizationId": self.org_id,
            "startRevision": 0
        }

        
        response = requests.post(
            f"{self.base_url}/api/1/nomenclature",
            headers=headers,
            json=body
        )

        print("Status code:", response.status_code)
        print("Response text:", response.text)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Помилка запиту меню: {response.status_code} {response.text}")
        

    def save_menu_from_db(self):
        data = self.get_menu()

        categories = [ cat for cat in data.get("productCategories", []) if not cat.get("isDeleted")]
        category_ids = [cat["id"] for cat in categories] 

        for cat in categories:
            ProductCategory.objects.update_or_create(
                id=cat["id"],
                defaults={
                    "name": cat["name"]
                }
            )

        ProductCategory.objects.exclude(id__in=category_ids).delete()

            
        groups = [gr for gr in data.get("groups", []) if not gr.get("isDeleted")]
        group_ids = [gr["id"] for gr in groups]

        for gr in groups:

            slug = self.generate_unique_slug(Group, gr.get("name", ""))

            Group.objects.update_or_create(
                id=gr["id"],
                defaults={
                    "name": gr.get("name", ""),
                    "slug": slug,
                    "parent_id": gr.get("parentGroup"),
                    "order": gr.get("order", 0),
                    "is_included_in_menu": gr.get("isIncludedInMenu", True),
                    "is_group_modifier": gr.get("isGroupModifier") is True,
                    "description": gr.get("description"),
                    "additional_info": gr.get("additionalInfo"),
                    "code": gr.get("code", ""),
                    "image_links": gr.get("imageLinks", []),
                    "tags": gr.get("tags", []),
                    "seo_title": gr.get("seoTitle"),
                    "seo_description": gr.get("seoDescription"),
                    "seo_text": gr.get("seoText"),
                    "seo_keywords": gr.get("seoKeywords"),

                }
            )

        Group.objects.exclude(id__in=group_ids).delete()




        products = [p for p in data.get("products", []) if not p.get("isDeleted")]
        product_ids = [] 

        for p in products:
            # Пропускаємо модифікатори і ті, що не в меню
            if p.get("type") != Product.DISH:
                continue
            if not p.get("sizePrices") or not p["sizePrices"][0].get("price", {}).get("isIncludedInMenu", True):
                continue

            product_ids.append(p["id"])


            # Визначаємо групу за parentGroup
            group = None
            if p.get("parentGroup"):
                group = Group.objects.filter(id=p["parentGroup"]).first()

            product_category = None
            if p.get("productCategoryId"):
                product_category = ProductCategory.objects.filter(id=p["productCategoryId"]).first()

            product_slug = self.generate_unique_slug(Product, p.get("name", ""))

            # Зберігаємо сам продукт
            product_obj, created = Product.objects.update_or_create(
                id=p["id"],
                defaults={
                    "code": p.get("code", ""),
                    "name": p.get("name", ""),
                    "slug": product_slug,
                    "description": p.get("description"),
                    "additional_info": p.get("additionalInfo"),
                    "group": group,
                    "product_category": product_category,
                    "type": p.get("type", Product.DISH),
                    "measure_unit": p.get("measureUnit", ""),
                    "weight": p.get("weight", 0.0),
                    "order": p.get("order", 0),
                    "payment_subject": p.get("paymentSubject", "ТОВАР"),
                    "image_url": p.get("imageLinks", [None])[0] if p.get("imageLinks") else None,
                    "seo_title": p.get("seoTitle"),
                    "seo_description": p.get("seoDescription"),
                    "seo_text": p.get("seoText"),
                    "seo_keywords": p.get("seoKeywords"),
                    "price": p.get("sizePrices", [{}])[0].get("price", {}).get("currentPrice", 0.0),
                    "is_included_in_menu": p.get("isIncludedInMenu", True)
                }           
            )
        Product.objects.exclude(id__in=product_ids).delete()

        # Обробка груп модифікаторів
        for gm in p.get("groupModifiers", []):
            group_mod, _ = GroupModifier.objects.update_or_create(
                id=gm["id"],
                defaults={
                    "product": product_obj,
                    "modifier_group_name": gm.get("modifierSchemaName", ""),
                    "min_amount": gm.get("minAmount", 0),
                    "max_amount": gm.get("maxAmount", 1),
                    "required": gm.get("required", False)
                }
            )

            # Дочірні модифікатори
            for child in gm.get("childModifiers", []):
                modifier_product = Product.objects.filter(id=child["id"]).first()
                if modifier_product:
                    GroupModifierChild.objects.update_or_create(
                        group_modifier=group_mod,
                        modifier=modifier_product,
                        defaults={
                            "default_amount": child.get("defaultAmount", 0),
                            "min_amount": child.get("minAmount", 0),
                            "max_amount": child.get("maxAmount", 0),
                            "required": child.get("required", False),
                            "hide_if_default_amount": child.get("hideIfDefaultAmount", False),
                            "splittable": child.get("splittable", False),
                            "free_of_charge_amount": child.get("freeOfChargeAmount", 0)
                        }
                    )
        

    def generate_unique_slug(self, model, name):
        """Генерує унікальний url з назви"""
        base_slug = slugify(name, allow_unicode=False)

        if not base_slug:
            base_slug = f"item-{uuid.uuid4().hex[:8]}"

        slug = base_slug
        counter = 1


        while model.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug


                




# categories = [cat for cat in data.get("productCategories", []) if not cat.get("isDeleted")]
# products = [prod for prod in data.get("products", []) if not prod.get("isDeleted")]


# if __name__ == "__main__":
#     client = SyrveClient()
#     menu = client.get_menu()
#     save = client.save_menu_from_db()

def run():
    """Точка входу для manage.py runscript"""
    client = SyrveClient()
    client.save_menu_from_db()
    print("✅ Меню успішно збережено у базу")