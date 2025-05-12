from pymongo import MongoClient
from bson import ObjectId
from Project1.Config.Config import connection_string_mongo

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(connection_string_mongo)
            self.db = self.client['My']
            self.initialize_products()
        except Exception as e:
            print(f"Помилка підключення до MongoDB: {e}")

    def initialize_products(self):
        """Якщо колекція Products порожня, заповнює її дефолтними продуктами."""
        collection = self.db['Products']
        if collection.count_documents({}) == 0:
            default_products = [
                {"name": "Laptop", "price": 1000, "stock_quantity": 10},
                {"name": "Smartphone", "price": 500, "stock_quantity": 20},
                {"name": "Headphones", "price": 100, "stock_quantity": 30},
                {"name": "PS5", "price": 2250, "stock_quantity": 30},
            ]
            for product in default_products:
                product['_id'] = ObjectId()
            collection.insert_many(default_products)
            print("Колекція Products була заповнена дефолтними продуктами.")
        else:
            print("Колекція Products вже містить дані.")

    def update_product_quantity_by_name(self, product_name, quantity):
        """Оновлює кількість товару за назвою"""
        collection = self.db['Products']
        result = collection.update_one(
            {"name": product_name},
            {"$inc": {"stock_quantity": quantity}}
        )
        if result.modified_count:
            print(f"Продукт '{product_name}' оновлено (кількість зміщено на {quantity}).")
            return True
        else:
            print(f"Продукт '{product_name}' не знайдено або оновлення не виконано.")
            return False

    def get_product_by_name(self, product_name):
        """Отримує дані продукту за назвою"""
        collection = self.db['Products']
        return collection.find_one({"name": product_name})

    def update_product_stock(self, product_name, quantity):
        """Зменшує запас товару на вказану кількість, якщо є достатньо"""
        collection = self.db['Products']
        result = collection.update_one(
            {"name": product_name, "stock_quantity": {"$gte": quantity}},
            {"$inc": {"stock_quantity": -quantity}}
        )
        return result.modified_count > 0

    def insert_order(self, order_data):
        """Вставляє замовлення в колекцію Orders"""
        collection = self.db['Orders']
        result = collection.insert_one(order_data)
        return result.inserted_id is not None