import json
import os
from datetime import date

EXPENSES_FILE = "data/expenses.json"
STORES_PRODUCTS_FILE = "data/stores_products.json"

def update_stores_and_products():
    """ Mağazalar ve ürün listesini günceller, yeni ürünleri ekler ve fiyatları günceller. """
    today = str(date.today())  # Günümüzün tarihi
    stores_data = {"stores": {}}  # Eğer dosya yoksa sıfırdan başla

    # **Mevcut Mağaza-Ürün Listesini Yükle**
    if os.path.exists(STORES_PRODUCTS_FILE):
        with open(STORES_PRODUCTS_FILE, "r", encoding="utf-8") as file:
            stores_data = json.load(file)

    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
            expenses = json.load(file).get("expenses", [])

        for expense in expenses:
            store = expense.get("store", "Genel")  # Mağaza yoksa 'Genel' olarak kabul et
            products = expense.get("items", [])

            if store not in stores_data["stores"]:
                stores_data["stores"][store] = {"products": {}}  # Yeni mağaza ekle

            for product in products:
                product_name = product.get("name")
                product_type = product.get("type", None)
                price = float(product.get("price", 0))  # Fiyat bilgisi

                if not product_name or price == 0:
                    continue  # Eksik ürünleri atla

                # JSON anahtar formatı: "ÜrünTipi_ÜrünAdı"
                product_key = f"{product_type}_{product_name}" if product_type else product_name

                # **Ürün zaten varsa fiyat geçmişini güncelle**
                if product_key in stores_data["stores"][store]["products"]:
                    stores_data["stores"][store]["products"][product_key]["price_history"][today] = price
                    stores_data["stores"][store]["products"][product_key]["latest_price"] = price
                else:
                    # **Yeni ürün eklenirse, fiyat geçmişi başlat**
                    stores_data["stores"][store]["products"][product_key] = {
                        "type": product_type,
                        "name": product_name,
                        "price_history": {today: price},
                        "latest_price": price
                    }

    # **Güncellenmiş JSON'u Kaydet**
    with open(STORES_PRODUCTS_FILE, "w", encoding="utf-8") as file:
        json.dump(stores_data, file, indent=4, ensure_ascii=False)